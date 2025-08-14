#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="themis",
    version="1.0.0",
    author="Miguel Gomes",
    author_email="miguel@example.com",
    description="Themis - Window management for Linux, based on Rectangle for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miguel/themis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment :: Window Managers",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.40.0",
        "pycairo>=1.20.0",
        "python-xlib>=0.31",
        "pynput>=1.7.0",
    ],
    entry_points={
        "console_scripts": [
            "themis=themis:main",
        ],
    },
    data_files=[
        ("share/applications", ["data/themis.desktop"]),
        ("share/pixmaps", ["data/themis.png"]),
        ("share/doc/themis", ["README.md", "LICENSE"]),
    ],
    include_package_data=True,
    zip_safe=False,
)