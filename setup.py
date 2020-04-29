from setuptools import setup, find_packages
import os.path
import re


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as fo:
        return fo.read()


def get_version():
    """
    Return package version as listed in `__version__` in `__init__.py`.
    """
    with open(os.path.join('xdutools', '__init__.py')) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]",
                         f.read()).group(1)


setup(
    name='xdu-tools',
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'lxml',
    ],
    entry_points='''
        [console_scripts]
        xdu=xdutools.cli:main
    ''',
)
