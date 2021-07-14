from QtToolsFish.Conans import QMake, QtConanFile
from QtToolsFish import conans_tools

if __name__ == '__main__':
    make = QMake("5.15.0", "x86", "release", pro_file="xxx.pro")
    make.build()
