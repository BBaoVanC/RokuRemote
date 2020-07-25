#!/usr/bin/env python3
"""
RokuRemote Layout Module

by bbaovanc

Library for different layouts
"""

# Imports
import importlib
import os


def load(layout: str):
    layoutobj = importlib.import_module(layout)
    print("Loaded layout: {0}".format(layoutobj.name))
    print("Author: {0}".format(layoutobj.author))
    print("Description: {0}".format(layoutobj.description))
    return layoutobj


def getlist(layoutdir="layouts"):
    if not type(layoutdir) == str:
        layoutdir = str(layoutdir)
    files = [f for f in os.listdir(layoutdir) if os.path.isfile("{0}/{1}".format(layoutdir, f))]

    layouts = []
    for filename in files:
        with open("{0}/{1}".format(layoutdir, filename)) as f:
            secondline = f.readlines()[1]
            if secondline.strip() == "# RokuRemoteLayout":
                layouts.append(filename)

    layouts2 = []
    for lay in layouts:
        lay2 = lay[:-3]
        layouts2.append(lay2)

    return layouts2
