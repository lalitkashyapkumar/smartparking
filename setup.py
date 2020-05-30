try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {

}

setup(**config, install_requires=['numpy', 'pytesseract'])
