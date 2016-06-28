import sys
import shutil
import os
from setuptools import setup, find_packages

CONF = os.getenv("SPIDER_CONF", "/etc/spider/main.yaml")

if len(sys.argv) > 0:
    if sys.argv[1] in ("install", "develop"):
        try:
            os.mkdir(os.path.dirname(CONF))
        except FileExistsError:
            print("Warning: {} directory already exists...".format(os.path.dirname(CONF)))
        print("Copying file to " + CONF)
        shutil.copy("conf/cobwebs.yaml", CONF)


import cobwebs


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
