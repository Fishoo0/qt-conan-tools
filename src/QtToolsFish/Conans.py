"""
Author: Fish

Currently, we only support 5.15.x vs2019

"""
import logging
import os

from conans import ConanFile, tools

from . import conans_tools


class QMake:
    build_cmd = ""

    def __init__(self, conanfile, qt_version=None, arch=None, build_type=None, pro_file=None, out_dir="%cd%",
                 vs_version="2019"):
        if qt_version is None:
            qt_version = conanfile.options.qt_version
        if arch is None:
            arch = conanfile.settings.arch
        if build_type is None:
            build_type = conanfile.settings.build_type
        if pro_file is None:
            pro_file = conanfile.get_src_folder()
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
    This is a Qt extended ConanFile, we follow the following file structure:
        -[source]
            -[self.name]
        -[build]
            -[self.name]
            -[self.build_type]
            -conaninfo.txt
            -conanbuildinfo.pri
        -[package]
            -[include]
            -[lib]
            -[bin]
            -[self.name]

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
    options = {"qt_version": ["5.12.4", "5.15.0", "5.15.2"]}
    default_options = {"qt_version": "5.15.0"}
    generators = "qmake", "cmake"

    # requires = "xxx/xxx"
    # exports_sources = "*"

    git_url = None
    git_branch = "master"
    enable_qt_debug_tail = False
    """
    Enable [self.name]d debug lib name.
    """
    enable_debug_and_release_one_package = False
    """
    Enable debug and rease in one package
    """

    header_only = False
    """
    The library only has only header, no cpp files.
    """

    def get_src_folder(self):
        """
        Getting default src dir
        :return: [self.name]
        """
        return f"./{self.name}/"

    @staticmethod
    def get_build_debug_folder():
        """
        Getting debug dir
        :return: [debug]
        """
        return "./debug/"

    @staticmethod
    def get_build_release_folder():
        """
        Getting release dir
        :return: [release]
        """
        return "./release/"

    def get_build_folder(self):
        """
        Getting dir from build_type, only support release & debug
        :return:
        """
        if self.settings.build_type == "Release":
            return self.get_build_release_folder()
        elif self.settings.build_type == "Debug":
            return self.get_build_debug_folder()
        else:
            raise Exception("Can not figure build dir")

    def configure(self):
        self.output.info("configure")
        if self.enable_debug_and_release_one_package:
            self.output.info("build_type is None, force enable debug_tail")
            self.enable_qt_debug_tail = True
        # self.requires.add("QtComposition/master", private=False)

    def package_id(self):
        self.output.info("package_id")
        if self.header_only:
            self.info.header_only()
            return
        if self.enable_debug_and_release_one_package:
            del self.info.settings.build_type
            del self.info.settings.compiler.runtime

    def source(self):
        self.output.info("source")
        if self.git_url is not None:
            conans_tools.git_clone(target_dir=f"{self.name}", url=self.git_url, branch=self.git_branch)
        if len(self.requires) > 0:
            self.output.info("requires length > 0, append conan requires ")
            conans_tools.add_conan_requires(
                pro_file=conans_tools.find_pro_file(conanfile=self, folder=self.get_src_folder()),
                folder="..")
        if self.enable_qt_debug_tail:
            self.output.info("enable_qt_debug_tail")
            conans_tools.enable_qt_debug_tail_d(
                pro_file=conans_tools.find_pro_file(conanfile=self, folder=self.get_src_folder()))

    def build(self):
        self.output.info("build")
        if self.header_only:
            return
        if self.enable_debug_and_release_one_package:
            self.output.info("build_type is none, build both debug & config")
            QMake(conanfile=self, build_type="Debug").build()
            QMake(conanfile=self, build_type="Release").build()
        elif self.settings.build_type == "Debug" or self.settings.build_type == "Release":
            self.output.info(f"build_type is -> {self.settings.build_type}")
            QMake(conanfile=self).build()
        else:
            raise Exception(f"Unsupported build type {self.settings.build_type}")

    def package(self):
        self.output.info("package")
        self.package_src()
        self.package_include()
        if not self.header_only:
            self.package_lib()
            self.package_bin()

    def package_src(self):
        self.output.info("package_src")
        conans_tools.copy_src(conanfile=self, folder=self.get_src_folder())

    def package_include(self):
        self.output.info("package_include")
        conans_tools.copy_includes(conanfile=self,
                                   folder=conans_tools.find_include_dir(folder=self.get_src_folder()))

    def package_lib(self):
        self.output.info("package_lib")
        if self.enable_debug_and_release_one_package:
            conans_tools.copy_lib(conanfile=self, folder=self.get_build_debug_folder())
            conans_tools.copy_lib(conanfile=self, folder=self.get_build_release_folder())
        else:
            conans_tools.copy_lib(conanfile=self, folder=self.get_build_folder())

    def package_bin(self):
        self.output.info("package_bin")
        if self.enable_debug_and_release_one_package:
            conans_tools.copy_bin(conanfile=self, folder=self.get_build_debug_folder())
            conans_tools.copy_bin(conanfile=self, folder=self.get_build_release_folder())
        else:
            conans_tools.copy_bin(conanfile=self, folder=self.get_build_folder())

    def package_info(self):
        self.output.info("package_info")
        if not self.header_only and self.enable_qt_debug_tail:
            self.collect_libs_with_qt_debug_tail()
        else:
            self.cpp_info.libs = tools.collect_libs(conanfile=self)

    def collect_libs_with_qt_debug_tail(self):
        """
        collect libs: debug -> {conanfile.name}d, release -> {conanfile.name}
        :return:
        """
        self.cpp_info.release.libs = [f"{self.name}"]
        self.cpp_info.debug.libs = [f"{self.name}d"]


class QtPreBuildConanFile(QtConanFile):
    """
    This class is designed for prebuild qt libs, and we follow the following file structure:
       -[source]
           -[self.name]
                -[inc/include]
                -[lib]
                -[bin]
           -conanfile.py
       -[build]
           -[self.name]
                -[inc/include]
                -[lib]
                -[bin]
           -conaninfo.txt
           -conanbuildinfo.pri
           -conanfile.py
       -[package]
           -[include]
           -[lib]
           -[bin]
    """

    enable_pure_c = False

    def configure(self):
        pass

    def package_id(self):
        super(QtPreBuildConanFile, self).package_id()
        if self.enable_pure_c:
            del self.info.options.qt_version

    def build(self):
        self.output.info("build pass")

    def package_src(self):
        self.output.info("package_src pass")

    def get_build_contents_folder(self, name):
        if self.enable_debug_and_release_one_package:
            temp_build_type = ""
        else:
            temp_build_type = f"{conans_tools.get_build_type_string_lower(conanfile=self)}"
        return f"{self.get_src_folder()}/{name}/{temp_build_type}/{conans_tools.get_arch_string_lower(conanfile=self)}"

    def package_lib(self):
        self.output.info("package_lib")
        conans_tools.copy_lib(conanfile=self, folder=self.get_build_contents_folder("lib"))

    def package_bin(self):
        self.output.info("package_bin")
        conans_tools.copy_bin(conanfile=self, folder=self.get_build_contents_folder("bin"))
