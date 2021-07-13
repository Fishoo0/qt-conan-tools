'''
Author: Fish

Currently, we only support 5.15.x vs2019

'''
import os

import conans
from conans import ConanFile


class QMake:
    build_cmd = ""

    def __init__(self, qt_version, arch, build_type, pro_file, out_dir="%cd%", vs_version="2019"):
        self.qt_version = qt_version
        self.arch = arch
        self.build_type = build_type
        self.pro_file = pro_file
        self.out_dir = out_dir
        self.vs_version = vs_version
        print("qt_version -> " + str(qt_version))
        print("arch -> " + str(arch))
        print("build_type -> " + str(build_type))
        print("pro_file -> " + str(pro_file))
        print("out_dir -> " + str(out_dir))
        print("vs_version -> " + str(vs_version))

    @classmethod
    def conan_file(cls, conan_file, out_dir="%cd%", vs_version="2019"):
        return cls(qt_version=conan_file.options.qt_version, arch=conan_file.settings.arch,
                   build_type=conan_file.settings.build_type, pro_file=conan_file.name, out_dir=out_dir,
                   vs_version=vs_version)

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

    def append_cmd(self, cmd):
        self.build_cmd += cmd
        self.build_cmd += " & "

    def setup_evn(self):
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

        if str(self.qt_version).startswith("5.15."):
            self.append_cmd(
                f"call \"{qt_home}\\{self.qt_version}\\msvc{self.vs_version}{qt_64_path}\\bin\\qtenv2.bat\"")
            self.append_cmd(f"call \"{vs_home}\\VC\\Auxiliary\\Build\\vcvars{vs_64_path}.bat\"")
        else:
            self.append_cmd(
                f"call \"%QT_HOME%\\{self.qt_version}\\msvc{self.vs_version}{qt_64_path}\\bin\\qtenv2.bat\"")
            self.append_cmd(f"call \"%VS{self.vs_version}_HOME%\\VC\\Auxiliary\\Build\\vcvars{vs_64_path}.bat\"")

    def build(self):
        print("Start to make project ...")
        self.setup_evn()
        self.append_cmd(f"cd {self.out_dir}")
        if self.is_debug():
            debug_config = "\"CONFIG+=debug\" \"CONFIG+=qml_debug\""
        else:
            debug_config = ""
        self.append_cmd(f"qmake {self.pro_file} -spec win32-msvc \"CONFIG+=qtquickcompiler\" {debug_config}")
        self.append_cmd("jom")
        print("cmd is -> " + self.build_cmd)
        os.system(self.build_cmd)
