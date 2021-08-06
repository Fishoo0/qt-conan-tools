from QtToolsFish import conans_tools
from QtToolsFish.Conans import QtConanFile

package_name = "qtpromise"
package_version = "v0.5.0"

package_user_channel = "cmguo/stable"


class ConanConfig(QtConanFile):
    name = package_name
    version = package_version

    git_url = "git@github.com:cmguo/qtpromise.git"

    header_only = True

    def package_include(self):
        print(f"src_folder -> {self.get_src_folder()}")
        self.copy("*", dst="include", src=f"{self.get_src_folder()}/include", keep_path=False)
        self.copy("*.h", dst="include", src=f"{self.get_src_folder()}/src", keep_path=False)
        self.copy("*", dst="src", src=f"./{self.get_src_folder()}/src")


if __name__ == '__main__':
    conans_tools.create(user_channel=package_user_channel, qt_versions_list=["5.15.0"], build_type_list=["Release"],
                        arch_list=["x86_64"])
    conans_tools.upload(package_version=f"{package_name}/{package_version}", user_channel=package_user_channel)
