import fnmatch
import logging
import os


def copy_src(conanfile, folder):
    """
    Copy src files to package: src_dir -> package/self.name
    :param folder:
    :param conanfile:
    :return:
    """
    conanfile.copy("*", dst=f"{conanfile.name}", src=folder, keep_path=True)


def copy_includes(conanfile, folder):
    """
    Copy includes from inculde_dir to package: include_dir -> package/include
    :param conanfile:
    :param folder: if include_dir is none, we would get include as the following sequence: conanfile.name/include -> conanfile.name/inc -> conanfile.name
    :return:
    """
    if folder.find("inc") == -1:
        conanfile.copy("*.h", dst="include", src=folder, keep_path=True)
        conanfile.copy("*.hpp", dst="include", src=folder, keep_path=True)
        conanfile.copy("*.hxx", dst="include", src=folder, keep_path=True)
    else:
        conanfile.copy("*", dst="include", src=folder, keep_path=True)


def copy_lib(conanfile, folder):
    """
    build_dir/libs -> package/libs
    :param conanfile:
    :param folder: if build_dir is None, set it to f"./{get_build_type_string(conanfile)}/"
    :return:
    """
    conanfile.copy("*.lib", dst="lib", src=folder, keep_path=False)
    conanfile.copy("*.exp", dst="lib", src=folder, keep_path=False)
    conanfile.copy("*.ini", dst="lib", src=folder, keep_path=False)
    conanfile.copy("*.dll", dst="lib", src=folder, keep_path=False)


def copy_bin(conanfile, folder):
    """
    build_dir/bins -> package/bins
    :param conanfile:
    :param folder: if build_dir is None, set it to f"./{get_build_type_string(conanfile)}/"
    :return:
    """
    conanfile.copy("*.a", dst="bin", src=folder, keep_path=False)
    conanfile.copy("*.so", dst="bin", src=folder, keep_path=False)
    conanfile.copy("*.dll", dst="bin", src=folder, keep_path=False)
    conanfile.copy("*.pdb", dst="bin", src=folder, keep_path=False)
    conanfile.copy("*.exe", dst="bin", src=folder, keep_path=False)


def get_arch_string_lower(conanfile):
    """
    :param conanfile:
    :return: x86 or x64
    """
    if conanfile.settings.arch == "x86_64":
        return "x64"
    else:
        return "x86"


def get_build_type_string_lower(conanfile):
    """
    :param conanfile:
    :return: debug or release
    """
    return str(conanfile.settings.build_type).lower()


def get_qt_version_string(conanfile):
    return str(conanfile.options.qt_version).lower()


def find_file_in_path(pattern, folder):
    result = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def add_conan_requires(pro_file, folder):
    """
    Adding conan requires if needed.
    :param folder:
    :param pro_file:
    :return:
    """
    with open(pro_file, 'r+') as f:
        content = f.read()
        if content is None or str(content).find("conan_basic_setup") == -1:
            f.seek(0, 0)
            f.write(f'''# This is an auto generation for add_conan_requires from conans_tools.
CONFIG += conan_basic_setup
include({folder}/conanbuildinfo.pri)

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


def find_pro_file(conanfile, folder):
    """
    Try to find pro file as our file structure.
    :return:
    """
    file_list = find_file_in_path(pattern="*.pro", folder=folder)
    print(f"find_pro_file -> {file_list}")
    if len(file_list) == 1:
        return file_list[0]
    elif len(file_list) <= 0:
        raise Exception(f"Can not find pro file in {folder}")
    else:
        for file in file_list:
            if str(file).lower().find(f"{conanfile.name}/{conanfile.name}".lower()) != -1:
                return file
    raise Exception(
        f"Can not figure pro file, multiple pro file has been found {file_list}. Maybe you should specify pro file path.")


def find_include_dir(folder):
    if os.path.exists(f"{folder}/include"):
        include_dir = f"{folder}/include"
    elif os.path.exists(f"{folder}/inc"):
        include_dir = f"{folder}/inc"
    else:
        include_dir = folder
    return include_dir


def git_clone(target_dir, url, branch="master"):
    """
    Clone projects to build/conanfile.name dir. This is import because the following file structure is base on it.
    :param target_dir:
    :param url:
    :param branch:
    :return:
    """
    os.system(f"git clone --depth 1 --single-branch --branch {branch} {url} {target_dir}")


def create(user_channel=None, build_type_list=["Release", "Debug"], arch_list=["x86", "x86_64"],
           qt_versions_list=["5.15.0", "5.15.2"]):
    """
    call conan create to create packages.
    :param user_channel:
    :param build_type_list:
    :param arch_list:
    :param qt_versions_list:
    :return:
    """
    if user_channel is None:
        user_channel = ""
    for arch in arch_list:
        for buildType in build_type_list:
            for qtVersion in qt_versions_list:
                logging.getLogger("QtTools").error(
                    f"QtConanTools: Starting creating arch {arch}, buildType {buildType}, qtVersion {qtVersion}")
                os.system(
                    f"conan create . {user_channel} -s arch={arch} -s build_type={buildType} -o qt_version={qtVersion}")


def upload(package_version, user_channel=None, server="tal-qt-repository-public", force=False):
    temp_user_channel = ""
    temp_force = ""
    if user_channel is not None:
        if str(user_channel).find("@") == -1:
            temp_user_channel = f"@{user_channel}"
        else:
            temp_user_channel = user_channel
    if force:
        temp_force = "--force"
    os.system(f"conan upload {package_version}{temp_user_channel} -r={server} {temp_force} --all --confirm")
