from QtToolsFish import conans_tools
from QtToolsFish.Conans import QtPreBuildConanFile

package_name = "QtHttpServer"
package_version = "1.0"

package_user_channel = "tal/stable"


class ConanConfig(QtPreBuildConanFile):
    name = package_name
    version = package_version
    exports_sources = "*"

    def get_src_folder(self):
        return f"./{self.options.qt_version}/"

    def get_build_contents_folder(self, name):
        return super(ConanConfig, self).get_build_contents_folder(name="lib")


if __name__ == '__main__':
    conans_tools.create(user_channel=package_user_channel, qt_versions_list=["5.15.0", "5.12.4"])
    conans_tools.upload(f"{package_name}/{package_version}", user_channel=package_user_channel)
