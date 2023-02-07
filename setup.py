from pathlib import Path
from typing import List
from setuptools import setup, find_packages

THIS_DIR = Path(__file__).parent

with open(THIS_DIR / "README.md", encoding="utf-8") as f:
    long_description = f.read()


def read_requirements(filepath: Path) -> List[str]:
    with open(filepath, encoding="utf-8") as fd:
        return [
            package.strip("\n")
            for package in fd.readlines()
            if not package.startswith("#")
        ]


def get_version(filepath: Path) -> str:
    with open(filepath, encoding="utf-8") as fd:
        for line in fd.readlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        raise RuntimeError("Unable to find version string.")


version = get_version(THIS_DIR / "labgraph" / "__init__.py")
requirements = read_requirements(THIS_DIR / "requirements.txt")
dev_requirements = read_requirements(THIS_DIR / "requirements-dev.txt")

setup(
    name="labgraph",
    version=version,
    description="A library for storing experimental materials science data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rishi Kumar",
    author_email="rekumar@lbl.gov",
    download_url="https://github.com/rekumar/alab_data",
    license="MIT",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
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
    # entry_points={
    #     'console_scripts': [
    #         'meg = megnet.cli.meg:main',
    #     ]
    # }
)
