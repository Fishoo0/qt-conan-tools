import os

from conans import ConanFile, tools
from . import QMake
from . import QtConanTools


class QtConanFile(ConanFile):
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

    def configure(self):
        self.log("configure")
        # self.requires.add("QtComposition/master", private=False)

    # def source(self):
    #   self.run("git clone git@github.com:cmguo/QtEventBus.git {}".format(self.name))
    #   QtConanTools.add_conan_requires(conan_file=self)

    def build(self):
        self.log("build")
        qmake = QMake.conan_file(conan_file=self)
        qmake.build()

    def package(self):
        self.log("package")
        QtConanTools.copy_structure_1(self)

    def package_info(self):
        self.log("package_info")
        self.cpp_info.libs = self.collect_libs()
