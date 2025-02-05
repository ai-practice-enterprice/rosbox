#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="rosbox-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "docker",
        "jinja2",
        "pick",
    ],
    entry_points={
        "console_scripts": [
            "rosbox=rosbox.rosbox:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rosbox": [
            "base_templates/*.jinja",
            "ros_templates/*.template",
            "entrypoints_templates/*.template",
            "entrypoints_templates/*.sh",
        ],
    },
    python_requires=">=3.7",
    description="CLI tool for managing ROS Docker environments",
    author="Arno Joosen",
)
