import logging
import os, fnmatch


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
    copy_src(conan_file=conan_file)
    copy_includes(conan_file=conan_file)
    copy_libs(conan_file=conan_file, build_dir=build_dir)
    copy_bins(conan_file=conan_file, build_dir=build_dir)


def copy_src(conan_file):
    """
    Copy src files to package: ./self.name -> package/self.name
    :param conan_file:
    :return:
    """
    conan_file.copy("*", dst=f"{conan_file.name}", src=f"./{conan_file.name}/", keep_path=True)


def copy_includes(conan_file, include_dir=None):
    """
    Copy includes from inculde_dir to package: include_dir -> package/include
    :param conan_file:
    :param include_dir: if include_dir is none, we would get include as the following sequence: conan_file.name/include -> conan_file.name/inc -> conan_file.name
    :return:
    """
    if include_dir is None:
        if os.path.exists(f"./{conan_file.name}/include"):
            include_dir = f"./{conan_file.name}/include"
        elif os.path.exists(f"./{conan_file.name}/inc"):
            include_dir = f"./{conan_file.name}/inc"
        else:
            include_dir = f"./{conan_file.name}/"

    if include_dir.find("inc") == -1:
        conan_file.copy("*.h", dst="include", src=include_dir, keep_path=True)
        conan_file.copy("*.hpp", dst="include", src=include_dir, keep_path=True)
    else:
        conan_file.copy("*", dst="include", src=include_dir, keep_path=True)


def copy_libs(conan_file, build_dir=None):
    """
    build_dir/libs -> package/libs
    :param conan_file:
    :param build_dir: if build_dir is None, set it to f"./{get_build_type_string(conan_file)}/"
    :return:
    """
    if build_dir is None:
        build_dir = f"./{get_build_type_string(conan_file)}/"
    conan_file.copy("*.lib", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.exp", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.ini", dst="lib", src=build_dir, keep_path=False)
    conan_file.copy("*.dll", dst="lib", src=build_dir, keep_path=False)


def copy_bins(conan_file, build_dir=None):
    """
    build_dir/bins -> package/bins
    :param conan_file:
    :param build_dir: if build_dir is None, set it to f"./{get_build_type_string(conan_file)}/"
    :return:
    """
    if build_dir is None:
        build_dir = f"./{get_build_type_string(conan_file)}/"
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


def find_file_in_path(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def find_pro_file(conan_file):
    dir = f"./{conan_file.name}/"
    file_list = find_file_in_path(pattern="*.pro", path=dir)
    print(f"find_pro_file -> {file_list}")
    if len(file_list) == 1:
        return file_list[0]
    elif len(file_list) <= 0:
        raise Exception(f"Can not find pro file in {dir}")
    else:
        for file in file_list:
            if str(file).lower().find(f"{conan_file.name}/{conan_file.name}".lower()) != -1:
                return file
    raise Exception(
        f"Can not figure pro file, multiple pro file has been found {file_list}. Maybe you should specify pro file path.")


def add_conan_requires(conan_file, pro_file=None):
    """
    Adding conan requires if needed.
    :param conan_file:
    :param pro_file:
    :return:
    """
    if pro_file is None:
        pro_file = find_pro_file(conan_file=conan_file)
    with open(pro_file, 'r+') as f:
        content = f.read()
        if content is None or str(content).find("conan_basic_setup") == -1:
            f.seek(0, 0)
            f.write('''# This is an auto generation for add_conan_requires from conans_tools.
CONFIG += conan_basic_setup
include(../conanbuildinfo.pri)

#End of auto generation
''' + content)


def enable_qt_debug_tail_d(conan_file, pro_file=None):
    """
    Add config for make
    :param conan_file:
    :param pro_file:
    :return:
    """
    if pro_file is None:
        pro_file = find_pro_file(conan_file=conan_file)
    with open(pro_file, 'r+') as f:
        content = f.read()
        if content is None or str(content).find("$$join(TARGET,,,d)") == -1:
            f.seek(0, 0)
            f.write(content + '''# This is an auto generation for enable_qt_debug_tail_d from conans_tools.
CONFIG(debug, debug|release) {
    TARGET = $$join(TARGET,,,d)
}
# End of auto generation
''')


def collect_libs_with_qt_debug_tail(conan_file):
    """
    collect libs: debug -> {conan_file.name}d, release -> {conan_file.name}

    :param conan_file:
    :return:
    """
    conan_file.cpp_info.release.libs = [f"{conan_file.name}"]
    conan_file.cpp_info.debug.libs = [f"{conan_file.name}d"]


def git_clone(conan_file, url, branch="master"):
    """
    Clone projects to build/conan_file.name dir. This is import because the following file structure is base on it.
    :param conan_file:
    :param url:
    :param branch:
    :return:
    """
    os.system(f"git clone --depth 1 --single-branch --branch {branch} {url} {conan_file.name}")


def create(build_type_list=["Release", "Debug"], arch_list=["x86", "x86_64"], qt_versions_list=["5.15.0"]):
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
                logging.getLogger("QtTools").error(
                    f"QtConanTools: Starting creating arch {arch}, buildType {buildType}, qtVersion {qtVersion}")
                os.system(
                    f"conan create . -s arch={arch} -s build_type={buildType} -o qt_version={qtVersion}")
