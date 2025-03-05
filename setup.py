#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of python-mediadecoder.

python-mediadecoder is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

QNotifications is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import os

from setuptools import setup, find_packages

path = os.path.dirname("__file__")
with open(os.path.join(path, "mediadecoder", "__init__.py")) as f:
    exec(f.readline().strip())

setup(
    name="mediadecoder",
    version=__version__,
    description="Moviepy based media decoding library",
    author="Daniel Schreij",
    author_email="dschreij@gmail.com",
    url="https://github.com/dschreij/python-mediadecoder",
    packages=find_packages("."),
    install_requires=[
        "moviepy",
        "numpy",
    ],
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Software Development :: Libraries :: pygame",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
