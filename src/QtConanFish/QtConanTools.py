import os


def copy_structure_1(conan_file):
    """
    This copy is for follow file structure:

        build_dir
                project_src_dir

                build_type_dir(debug/release)

        project_src_dir -> package/project_src_dir

        project_src_dir/*.h,*.hpp -> package/include

        build_type_dir/libs -> package/libs

        build_type_dir/bins -> package/bins

    :param conan_file:
    :return:
    """
    print("copy_structure_1")
    conan_file.copy("*", dst=f"{conan_file.name}", src=f"./{conan_file.name}/", keep_path=True)

    conan_file.copy("*.h", dst="include", src=f"./{conan_file.name}/")
    conan_file.copy("*.hpp", dst="include", src=f"./{conan_file.name}/")

    build_dir = f"./{get_build_type_string(conan_file)}/"
    copy_libs(conan_file=conan_file, build_dir=build_dir)
    copy_bins(conan_file=conan_file, build_dir=build_dir)


def copy_structure_2(conan_file):
    """
    This copy is for follow file structure:

        build_dir
                project_src_dir

                build_type_dir(debug/release)

        project_src_dir -> package/project_src_dir

        project_src_dir/include,inc -> package/include

        build_type_dir/libs -> package/libs

        build_type_dir/bins -> package/bins

    :param conan_file:
    :return:
    """
    print("copy_structure_2")
    conan_file.copy("*", dst=f"{conan_file.name}", src=f"./{conan_file.name}/", keep_path=True)
    conan_file.copy("*", dst="include", src=f"./{conan_file.name}/include")
    conan_file.copy("*", dst="include", src=f"./{conan_file.name}/inc")
    build_dir = f"./{get_build_type_string(conan_file)}/"
    copy_libs(conan_file=conan_file, build_dir=build_dir)
    copy_bins(conan_file=conan_file, build_dir=build_dir)


def copy_libs(conan_file, build_dir):
    """
    build_dir/libs -> package/libs
    :param conan_file:
    :param build_dir:
    :return:
    """
    if build_dir is None:
        raise Exception("Invalid build_dir")
    conan_file.copy("*.lib", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.exp", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.ini", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.dll", dst="lib", src=build_dir, keep_path=False)


def copy_bins(conan_file, build_dir):
    """
    build_dir/bins -> package/bins
    :param conan_file:
    :param build_dir:
    :return:
    """
    if build_dir is None:
        raise Exception("Invalid build_dir")
    conan_file.copy("*.a", dst="bin", src=build_dir, keep_path=False)
    conan_file.copy("*.so", dst="bin", src=build_dir, keep_path=False)
    conan_file.copy("*.dll", dst="bin", src=build_dir, keep_path=False)
    conan_file.copy("*.pdb", dst="bin", src=build_dir, keep_path=False)


def get_arch_string(conan_file):
    """

    :param conan_file:
    :return: x86 or x64
    """
    if conan_file.settings.arch == "x86_64":
        return "x64"
    else:
        return "x86"


def get_build_type_string(conan_file):
    """
    :param conan_file:
    :return: debug or release
    """
    return str(conan_file.settings.build_type).lower()


def get_qt_version_string(conan_file):
    return str(conan_file.options.qt_version).lower()


def add_conan_requires(conan_file):
    """
    Adding conan requires if needed.
    :param conan_file:
    :return:
    """
    add_conan_requires(pro_file=f"{conan_file.name}/{conan_file.name}.pro")


def add_conan_requires(pro_file):
    """
    Adding conan requires if needed.
    :param pro_file:
    :return:
    """
    with open(pro_file, 'r+') as f:
        content = f.read()
        if content is None or str(content).find("conan_basic_setup") == -1:
            f.seek(0, 0)
            f.write('''# This is an auto generation for conan requires.
CONFIG += conan_basic_setup
include(../conanbuildinfo.pri)

''' + content)


#     tools.replace_in_file(pro_file, "TEMPLATE = lib",
#                           '''TEMPLATE = lib
# CONFIG += conan_basic_setup
# include(../conanbuildinfo.pri)
# ''')


def create(build_type_list=["Release", "Debug"], arch_list=["x86", "x64"], qt_versions_list=["5.15.0"]):
    """
    call conan create to create packages.
    :param build_type_list:
    :param arch_list:
    :param qt_versions_list:
    :return:
    """
    for arch in arch_list:
        for buildType in build_type_list:
            for qtVersion in qt_versions_list:
                print(f"QtConanTools: Starting creating arch {arch}, buildType {buildType}, qtVersion {qtVersion}")
                os.system(
                    f"conan create . -s arch={arch} -s build_type={buildType} -o qt_version={qtVersion}")
