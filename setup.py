#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="netpulse",
    version="1.1.1",
    description="Network monitoring tool for Raspberry Pi",
    author="Vector",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.2.2",
        "click>=8.1.3", 
        "Jinja2>=3.1.0",
        "Werkzeug>=2.2.2",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "netpulse=netpulse.web:main",
            "netpulse-measure=netpulse.speedtest:main",
        ],
    },
    include_package_data=True,
    package_data={
        "netpulse": [
            "templates/*.html",
            "static/css/*.css",
            "static/icons/*",
            "static/js/*.js",
        ],
    },
    data_files=[
        ("/etc/netpulse", ["config/default.conf"]),
        ("/lib/systemd/system", ["systemd/netpulse.service", "systemd/netpulse.timer", "systemd/netpulse-web.service"]),
    ],
    zip_safe=False,
    use_2to3=False,
    options={
        'bdist_wheel': {
            'universal': 0,
        }
    },
)
