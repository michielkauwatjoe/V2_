"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

NAME = 'MoveMe'
VERSION = '0.1'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='v2.nl',
)

setup(
    #data_files=['English.lproj', 'data'],
    data_files=['data'],
    app=[
        dict(script="MultiPillow.py", plist=plist),
    ],
)
