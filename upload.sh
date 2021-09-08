#!C:\Program Files\Git\bin\bash.exe
export http_proxy=8.8.8.8:8888
rm -rf dist
py -m build
twine upload --repository testpypi dist/*