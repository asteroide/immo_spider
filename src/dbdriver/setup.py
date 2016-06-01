from setuptools import setup, find_packages
import dbdriver

setup(

    name='dbdriver',

    version=dbdriver.__version__,

    packages=find_packages(),

    author="Asteroide",

    author_email="asteroide__AT__domtombox.net",

    description="An API server",

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