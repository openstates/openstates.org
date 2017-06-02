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
      ],
      entry_points={
        'console_scripts': ['admintools = admintools.cli:main'],
      },
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   ],
      )
