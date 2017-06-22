#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="admintools",
      version='0.1',
      license="MIT",
      description="opencivicdata admin tools",
      long_description="",
      url="",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
            'Django>=1.11',
            'pupa>=0.6',
            'opencivicdata>=1.0',
            'flake8',
      ],
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.5",
                   ],
      )
