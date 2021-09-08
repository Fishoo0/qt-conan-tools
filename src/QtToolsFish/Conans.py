"""
Author: Fish

Currently, we only support 5.15.x vs2019

"""
import os

from conans import ConanFile, tools

from .Qt import QMake
from . import conans_tools


class QtConanFile(ConanFile):
    """
    This is a Qt extended ConanFile, we follow the following file structure:
        -[source]
            -[self.get_library_name()]
        -[build]
            -[self.get_library_name()]
            -[self.build_type]
            -conaninfo.txt
            -conanbuildinfo.pri
        -[package]
            -[include]
            -[lib]
            -[bin]
            -[self.get_library_name()]

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
    Enable [self.get_library_name()]d debug lib name.
    """
    enable_debug_and_release_one_package = False
    """
    Enable debug and rease in one package
    """

    header_only = False
    """
    The library only has only header, no cpp files.
    """

    def get_library_name(self):
        return f"{self.name}"

    def get_src_folder(self):
        """
        Getting default src dir
        :return: get_library_name()
        """
        return f"./{self.get_library_name()}/"

    @staticmethod
    def get_build_debug_folder():
        """
        Getting debug dir
        :return: [debug]
        """
        target_path = "./debug/"
        if os.path.exists(target_path) and os.path.isdir(target_path) and len(os.listdir(target_path)) > 0:
            return target_path
        return "./"

    @staticmethod
    def get_build_release_folder():
        """
        Getting release dir
        :return: [release]
        """
        target_path = "./release/"
        if os.path.exists(target_path) and os.path.isdir(target_path) and len(os.listdir(target_path)) > 0:
            return target_path
        return "./"

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
        if self.git_url is not None and self.exports_sources is None:
            conans_tools.git_clone(target_dir=self.get_library_name(), url=self.git_url, branch=self.git_branch)
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
            QMake(qt_version=self.options.qt_version, arch=self.settings.arch, build_type="Debug",
                  pro_file=self.get_src_folder()).build()
            QMake(qt_version=self.options.qt_version, arch=self.settings.arch, build_type="Release",
                  pro_file=self.get_src_folder()).build()
        elif self.settings.build_type == "Debug" or self.settings.build_type == "Release":
            self.output.info(f"build_type is -> {self.settings.build_type}")
            QMake(qt_version=self.options.qt_version, arch=self.settings.arch,
                  build_type=self.settings.build_type, pro_file=self.get_src_folder()).build()
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
        self.cpp_info.release.libs = [self.get_library_name()]
        self.cpp_info.debug.libs = [f"{self.get_library_name()}d"]


class QtPreBuildConanFile(QtConanFile):
    """
    This class is designed for prebuild qt libs, and we follow the following file structure:
       -[source]
           -[self.get_library_name()]
                -[inc/include]
                -[lib]
                -[bin]
           -conanfile.py
       -[build]
           -[self.get_library_name()]
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
