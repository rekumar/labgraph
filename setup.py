from pathlib import Path
from setuptools import setup
from setuptools import find_packages
import os
from alab_data.metadata import (
    __version__,
    __description__,
    __author__,
    __author_email__,
    __license__,
)

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# with open('megnet/__init__.py', encoding='utf-8') as fd:
#     try:
#         lines = ''
#         for item in fd.readlines():
#             item = item
#             lines += item + '\n'
#     except Exception as exc:
#         raise Exception('Caught exception {}'.format(exc))


# version = re.search('__version__ = "(.*)"', lines).group(1)


setup(
    name="alab_data",
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__author_email__,
    download_url="https://github.com/rekumar/alab_data",
    license=__license__,
    python_requires=">=3.8",
    install_requires=[
        package.strip("\n")
        for package in (Path(__file__).parent / "requirements.txt")
        .open("r", encoding="utf-8")
        .readlines()
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords=[
        "materials",
        "science",
        "machine",
        "automation",
        "data",
        "mongodb",
        "storage",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "alab_data = alab_data.scripts.cli:cli",
        ]
    },
)
