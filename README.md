# About Me
    Bring qt feature to ConanFile, witch is called QtConanFile

# Basic Usage
### Create pip package by [TestPypi](https://packaging.python.org/guides/using-testpypi/)
    1, python -m build
    2, twine upload --repository testpypi dist/*
    3, enjoy

### Downloading package
    1, pip install -i https://test.pypi.org/simple/ qt-tools-fish-test1 --upgrade 
       or pip install -i https://test.pypi.org/simple/ your-package-name --upgrade

### Creat Your ConanFile
    DemoConanFile(QtConanFile), see demo dir for detail.
    
# Advantage Usage
### Behind Logic
    1, Class 'QMake' help to compile Qt .pro project
    2, Fixed file sturcture: (Read QtConanFile for detail)
        -build
            -project_name
                - project_name.pro
                - files ...
    3, conans_tools.py wraps some convenient functions

### Tips
    If you want more control of this, you should read QtConanFile, witch is very easy for understanding



# About Author
    Fish, mail: 790105840@qq.com