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
    layoutobj = importlib.import_module(layout)  # import the layout
    print("Loaded layout: {0}".format(layoutobj.name))
    print("Author: {0}".format(layoutobj.author))
    print("Description: {0}".format(layoutobj.description))
    return layoutobj  # return the layout


def getlist(layoutdir="layouts"):
    if not type(layoutdir) == str:
        layoutdir = str(layoutdir)  # convert the layout directory to a string

    # remove anything that doesn't exist
    files = [f for f in os.listdir(layoutdir) if os.path.isfile("{0}/{1}".format(layoutdir, f))]

    layouts = []  # initialize layouts variable as list
    for filename in files:  # for each file
        with open("{0}/{1}".format(layoutdir, filename)) as f:
            secondline = f.readlines()[1]
            if secondline.strip() == "# RokuRemoteLayout":  # if the file is marked as a layout
                layouts.append(filename)  # add the file to the list of layouts

    layouts2 = []
    for lay in layouts:
        lay2 = lay[:-3]  # remove the last 3 characters (.py)
        layouts2.append(lay2)

    return layouts2
