from pathlib import Path
from typing import List
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


def parse_requirements(filename: str) -> List[str]:
    """load requirements from a pip requirements file"""
    filepath = Path(__file__).parent / filename
    with open(filepath, "r") as f:
        packages = [line.strip() for line in f if line and not line.startswith("#")]
    return packages


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
    install_requires=parse_requirements("requirements.txt"),
    extras_require={"dev": parse_requirements("requirements-dev.txt")},
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
