# pylint: disable=missing-docstring
import re

from setuptools import setup

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("src/apprec/__init__.py", "r") as f:
    VERSION_MATCH = re.search(r"__version__ = \"(.*?)\"", f.read())
    if VERSION_MATCH:
        VERSION = VERSION_MATCH.group(1)

setup(
    name="apprec",
    version=VERSION,
    author="Marvin Steadfast",
    author_email="marvin@xsteadfastx.org",
    description="record pulseaudio output in an easy way",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=["apprec"],
    package_dir={"": "src"},
    package_data={},
    include_package_data=True,
    install_requires=["click>=6.7", "logzero>=1.5", "pulsectl>=18.8"],
    entry_points="""
        [console_scripts]
        apprec=apprec.cli:main
    """,
)
