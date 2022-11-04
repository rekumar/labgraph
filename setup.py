from setuptools import setup
from setuptools import find_packages
import os

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
    version="0.1.0",
    description="A library for storing experimental materials science data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rishi Kumar",
    author_email="rekumar@lbl.gov",
    download_url="https://github.com/rekumar/alab_data",
    license="MIT",
    install_requires=[
        "numpy",
        "matplotlib",
        "networkx",
        "pymongo",
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
    # entry_points={
    #     'console_scripts': [
    #         'meg = megnet.cli.meg:main',
    #     ]
    # }
)
