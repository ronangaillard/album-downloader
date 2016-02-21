from distutils.core import setup
from setuptools import setup

setup(
    # Application name:
    name="album-dl",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Ronan_Gaillard",
    author_email="ronan.gaillard@supelec.fr",
    
    #scripts=['album-dl.py'],

    # Packages
    packages=["albumdownloader"],

    # Include additional files into the package
    #include_package_data=True,

    # Details
    url="http://ronan.gaillard.free.fr",

    #
    # license="LICENSE.txt",
    description="Python application to download full music albums using LastFM and Youtube",

    # Dependent packages (distributions)
    install_requires=[
        "requests",
        "mutagen",
        "youtube-dl"
    ],
    
    entry_points = {
        'console_scripts': [
            'album-dl=albumdownloader.__main__:main',
        ],
    },
)