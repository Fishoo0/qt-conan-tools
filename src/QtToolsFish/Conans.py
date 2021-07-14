'''
Author: Fish

Currently, we only support 5.15.x vs2019

'''
import logging
import os

from conans import ConanFile

from . import conans_tools


class QMake:
    build_cmd = ""

    def __init__(self, conan_file, qt_version=None, arch=None, build_type=None, pro_file=None, out_dir="%cd%",
                 vs_version="2019"):
        if qt_version is None:
            qt_version = conan_file.options.qt_version
        if arch is None:
            arch = conan_file.settings.arch
        if build_type is None:
            build_type = conan_file.settings.build_type
        if pro_file is None:
            pro_file = conan_file.name
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
        logging.getLogger("QtTools").error("cmd is -> " + self.build_cmd)
        os.system(self.build_cmd)


class QtConanFile(ConanFile):
    """
    This is a Qt extended ConanFile
    """
    TAG = "QtConanFile"
    name = "Your Project Name"
    version = "master"
    license = "All rights by fish"
    author = "Fish"
    url = "https://www.github.com"
    description = "This is a library from fish."
    topics = ("qt", "conan", "library")
    settings = "os", "compiler", "build_type", "arch"
    options = {"qt_version": ["5.15.0", "5.15.2"]}
    default_options = {"qt_version": "5.15.0"}
    generators = "qmake", "cmake"

    # requires = "xxx/xxx"
    # exports_sources = "*"

    def log(self, msg):
        print(f"{self.TAG}: {msg}")

    # def package_id(self):
    #     del self.info.settings.build_type

    def configure(self):
        self.log("configure")
        # self.requires.add("QtComposition/master", private=False)

    def source(self):
        self.log("source")
        # conans_tools.git_clone(conan_file=self, url="xxx.git", branch="master")
        # conans_tools.add_conan_requires(conan_file=self, pro_file=f"{self.name}/{str(self.name).lower()}.pro")
        #
        #     tools.replace_in_file(pro_file, "TEMPLATE = lib",
        #                           '''TEMPLATE = lib
        # CONFIG += conan_basic_setup
        # include(../conanbuildinfo.pri)
        # ''')

    def build(self):
        self.log("build")
        # QMake(conan_file=self).build()

    def package(self):
        self.log("package")
        conans_tools.copy_structure_1(self)

    def package_info(self):
        self.log("package_info")
        self.cpp_info.libs = self.collect_libs()
        # conans_tools.collect_libs_with_qt_debug_tail(conan_file=self)

