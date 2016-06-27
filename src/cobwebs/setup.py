import sys
import shutil
import os
from setuptools import setup, find_packages
import cobwebs
import subprocess


if len(sys.argv) > 0:
    if sys.argv[1] in ("install", "develop"):
        try:
            os.mkdir("/etc/spider/")
        except FileExistsError:
            print("Warning: /etc/spider directory already exists...")
        print("Copying file to /etc/spider/")
        ret = shutil.copy("conf/cobwebs.yaml", "/etc/spider/cobwebs.yaml")
        print(ret)
        subprocess.call(["ls", "-l", "/etc/spider"])

setup(

    name='cobwebs',

    version=cobwebs.__version__,

    packages=find_packages(),

    author="Asteroide",

    author_email="asteroide__AT__domtombox.net",

    description="A house for spider utilities",

    long_description=open('README.md').read(),

    # install_requires= ,

    include_package_data=True,

    url='https://github.com/asteroide/immo_spider',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],

)
