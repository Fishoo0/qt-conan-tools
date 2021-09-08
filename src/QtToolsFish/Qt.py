import logging
import os

from sys import platform


class QMake:
    build_cmd = ""

    def __init__(self, qt_version=None, arch="x86_64", build_type="Release", pro_file="./", out_dir=None,
                 vs_version="2019"):
        if qt_version is None:
            raise Exception("qt_version must be set !")
        if pro_file is None:
            raise Exception("pro_file must be set !")
        self.qt_version = qt_version
        self.arch = arch
        self.build_type = build_type
        self.pro_file = pro_file
        if out_dir is None:
            if platform == "linux" or platform == "linux2":
                out_dir = None
            elif platform == "darwin":
                out_dir = None
            elif platform == "win32":
                out_dir = "%cd%"
        self.out_dir = out_dir
        self.vs_version = vs_version

        print("qt_version -> " + str(qt_version))
        print("arch -> " + str(arch))
        print("build_type -> " + str(build_type))
        print("pro_file -> " + str(pro_file))
        print("out_dir -> " + str(out_dir))
        print("vs_version -> " + str(vs_version))

    def is_x64(self):
        if str(self.arch).lower().find("64") == -1:
            return False
        else:
            return True

    def is_debug(self):
        if str(self.build_type).lower() == "debug":
            return True
        else:
            return False

    def append_cmd(self, cmd, last=False):
        self.build_cmd += cmd
        if not last:
            if platform == "win32":
                self.build_cmd += " & "
            else:
                self.build_cmd += " && "

    def build_darwin(self):
        print("build_darwin")
        # setup evn
        qt_home = os.getenv('QT_HOME')
        if qt_home is None:
            qt_home = f"{os.getenv('HOME')}/Qt"
            if not os.path.exists(qt_home):
                raise Exception(
                    f"Can not found QT_HOME dir! Install Qt in {qt_home}, otherwise you must set QT_HOME system evn. ")
        print("qt_home -> " + qt_home)
        self.append_cmd(f"export PATH=$PATH:{qt_home}/{self.qt_version}/clang_64/bin")
        # start build
        if self.out_dir is not None:
            self.append_cmd(f"cd {self.out_dir}")
        self.append_cmd(f"qmake -v")
        if self.is_debug():
            debug_config = "\"CONFIG+=debug\" \"CONFIG+=qml_debug\""
        else:
            debug_config = ""
        self.append_cmd(f"qmake {self.pro_file} -spec macx-clang \"CONFIG+=qtquickcompiler\" {debug_config}")
        self.append_cmd("make -j8", last=True)
        logging.getLogger("QtTools").error("cmd is -> " + self.build_cmd)
        os.system(self.build_cmd)

    def build_linux(self):
        print("build_linux")
        pass

    def build_win(self):
        print("build_win")
        print("setup_evn_windows")
        qt_home = os.getenv('QT_HOME')
        vs_home = os.getenv(f'VS{self.vs_version}_HOME')
        if qt_home is None:
            qt_home = "C:\\Qt"
            if not os.path.exists(qt_home):
                raise Exception(
                    f"Can not found QT_HOME dir! Install Qt in {qt_home}, otherwise you must set QT_HOME system evn. ")
        if vs_home is None:
            vs_home = f"C:\\Program Files (x86)\\Microsoft Visual Studio\\{self.vs_version}\\Professional"
            if not os.path.exists(vs_home):
                raise Exception(
                    f"Can not found VS{self.vs_version}_HOME dir! Install Qt in {vs_home}, otherwise you must set VS{self.vs_version}_HOME system evn. ")
        print("qt_home -> " + qt_home)
        print("vs_home -> " + vs_home)
        if self.is_x64():
            qt_64_path = "_64"
            vs_64_path = "64"
        else:
            qt_64_path = ""
            vs_64_path = "32"
        self.append_cmd(f"set PATH={qt_home}\Tools\QtCreator\\bin;%PATH%")
        if str(self.qt_version).startswith("5.15."):
            self.append_cmd(
                f"call \"{qt_home}\\{self.qt_version}\\msvc{self.vs_version}{qt_64_path}\\bin\\qtenv2.bat\"")
            self.append_cmd(f"call \"{vs_home}\\VC\\Auxiliary\\Build\\vcvars{vs_64_path}.bat\"")
        else:
            self.append_cmd(
                f"call \"%QT_HOME%\\{self.qt_version}\\msvc{self.vs_version}{qt_64_path}\\bin\\qtenv2.bat\"")
            self.append_cmd(f"call \"%VS{self.vs_version}_HOME%\\VC\\Auxiliary\\Build\\vcvars{vs_64_path}.bat\"")
        # start build
        self.append_cmd(f"cd {self.out_dir}")
        if self.is_debug():
            debug_config = "\"CONFIG+=debug\" \"CONFIG+=qml_debug\""
        else:
            debug_config = ""
        self.append_cmd(f"qmake {self.pro_file} -spec win32-msvc \"CONFIG+=qtquickcompiler\" {debug_config}")
        self.append_cmd("jom")
        logging.getLogger("QtTools").error("cmd is -> " + self.build_cmd)
        os.system(self.build_cmd)

    def build(self):
        if platform == "linux" or platform == "linux2":
            self.build_linux()
        elif platform == "darwin":
            self.build_darwin()
        elif platform == "win32":
            self.build_win()
