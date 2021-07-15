import fnmatch
import logging
import os


def copy_src(conan_file, src_dir):
    """
    Copy src files to package: src_dir -> package/self.name
    :param src_dir:
    :param conan_file:
    :return:
    """
    conan_file.copy("*", dst=f"{conan_file.name}", src=src_dir, keep_path=True)


def copy_includes(conan_file, include_dir):
    """
    Copy includes from inculde_dir to package: include_dir -> package/include
    :param conan_file:
    :param include_dir: if include_dir is none, we would get include as the following sequence: conan_file.name/include -> conan_file.name/inc -> conan_file.name
    :return:
    """
    if include_dir.find("inc") == -1:
        conan_file.copy("*.h", dst="include", src=include_dir, keep_path=True)
        conan_file.copy("*.hpp", dst="include", src=include_dir, keep_path=True)
        conan_file.copy("*.hxx", dst="include", src=include_dir, keep_path=True)
    else:
        conan_file.copy("*", dst="include", src=include_dir, keep_path=True)


def copy_lib(conan_file, lib_dir):
    """
    build_dir/libs -> package/libs
    :param conan_file:
    :param lib_dir: if build_dir is None, set it to f"./{get_build_type_string(conan_file)}/"
    :return:
    """
    conan_file.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
    conan_file.copy("*.exp", dst="lib", src=lib_dir, keep_path=False)
    conan_file.copy("*.ini", dst="lib", src=lib_dir, keep_path=False)
    conan_file.copy("*.dll", dst="lib", src=lib_dir, keep_path=False)


def copy_bin(conan_file, bin_dir):
    """
    build_dir/bins -> package/bins
    :param conan_file:
    :param bin_dir: if build_dir is None, set it to f"./{get_build_type_string(conan_file)}/"
    :return:
    """
    conan_file.copy("*.a", dst="bin", src=bin_dir, keep_path=False)
    conan_file.copy("*.so", dst="bin", src=bin_dir, keep_path=False)
    conan_file.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
    conan_file.copy("*.pdb", dst="bin", src=bin_dir, keep_path=False)


def get_arch_string_lower(conan_file):
    """
    :param conan_file:
    :return: x86 or x64
    """
    if conan_file.settings.arch == "x86_64":
        return "x64"
    else:
        return "x86"


def get_build_type_string_lower(conan_file):
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


def add_conan_requires(pro_file, conanbuildinfo_dir):
    """
    Adding conan requires if needed.
    :param conanbuildinfo_dir:
    :param pro_file:
    :return:
    """
    with open(pro_file, 'r+') as f:
        content = f.read()
        if content is None or str(content).find("conan_basic_setup") == -1:
            f.seek(0, 0)
            f.write(f'''# This is an auto generation for add_conan_requires from conans_tools.
CONFIG += conan_basic_setup
include({conanbuildinfo_dir}/conanbuildinfo.pri)

#End of auto generation
''' + content)


def enable_qt_debug_tail_d(pro_file=None):
    """
    Add config for make
    :param pro_file:
    :return:
    """
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


def find_pro_file(conan_file, src_dir):
    """
    Try to find pro file as our file structure.
    :return:
    """
    file_list = find_file_in_path(pattern="*.pro", path=src_dir)
    print(f"find_pro_file -> {file_list}")
    if len(file_list) == 1:
        return file_list[0]
    elif len(file_list) <= 0:
        raise Exception(f"Can not find pro file in {src_dir}")
    else:
        for file in file_list:
            if str(file).lower().find(f"{conan_file.name}/{conan_file.name}".lower()) != -1:
                return file
    raise Exception(
        f"Can not figure pro file, multiple pro file has been found {file_list}. Maybe you should specify pro file path.")


def find_include_dir(src_dir):
    if os.path.exists(f"./{src_dir}/include"):
        include_dir = f"./{src_dir}/include"
    elif os.path.exists(f"./{src_dir}/inc"):
        include_dir = f"./{src_dir}/inc"
    else:
        include_dir = f"./{src_dir}/"
    return include_dir


def git_clone(target_dir, url, branch="master"):
    """
    Clone projects to build/conan_file.name dir. This is import because the following file structure is base on it.
    :param target_dir:
    :param url:
    :param branch:
    :return:
    """
    os.system(f"git clone --depth 1 --single-branch --branch {branch} {url} {target_dir}")


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
