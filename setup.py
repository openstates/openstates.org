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
            'opencivicdata',
            'flake8',
      ],
      dependency_links=[
            'git+https://github.com/opencivicdata/python-opencivicdata.git@879d73b94557c63332f0c7ca2d70984810c64734#egg=opencivicdata-dev'
      ],
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.5",
                   ],
      )
