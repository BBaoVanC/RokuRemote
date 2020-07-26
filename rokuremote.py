#!/usr/bin/env python3
"""
RokuRemote

by bbaovanc

Program to control a Roku using your computer
"""

# Imports
from multiprocessing.dummy import Pool  # Used for async requests

import urllib  # Used here for percent encoding
import readchar  # Library to read single characters of input
import pprint

import layouts
import libroku

pool = Pool(50)  # Create async task pool
pprinter = pprint.PrettyPrinter(indent=4)


def on_error(error):  # Called when an error occurs in HTTP requests
    print("POST ERROR")
    print(error)


# Functions for command mode
def setlayout(new):
    global layout
    if len(new) > 0:
        if not new.startswith("layouts."):
            args2 = "layouts.{0}".format(new)
        else:
            args2 = new
        try:
            layout = layouts.load(args2)
        except ModuleNotFoundError as e:
            print("ERR: ModuleNotFoundError - error information below:")
            print(e)

    else:
        print("ERR: No layout specified.")
        print("Current layout: {0}".format(layout.name))
        print("List all layouts by typing :listlayouts")


def listlayouts(arg=None):
    print("Valid layouts: {0}".format(", ".join(map(str, layouts.getlist()))))
    print("Use :setlayout to change layouts.")


def search(keywords):
    libroku.sendsearch(pool, host, keywords, on_error)


def commands(arg=None):
    print("Valid commands: {0}".format(", ".join(map(str, commandmap.keys()))))


def chooselayout(arg=None):
    laylist = layouts.getlist()
    print("Type the number corresponding to the layout you want to use:")
    for a in range(len(laylist)):
        print("[{0}] {1}".format(a, laylist[a]))

    sel = input("> ")
    selint = int(sel)
    if selint in list(range(len(laylist))):
        print("Selected: {0}".format(laylist[selint]))
        setlayout(laylist[selint])
    else:
        print("Invalid selection.")


def viewlayout(view):
    global layout
    splitarg = view.split()
    valuefound = False
    if len(splitarg) > 1:
        if splitarg[0] == "find":
            findkw = splitarg[1]
            for key, value in layout.buttonmap.items():
                if value.lower() == findkw.lower():
                    print("{0} is bound to {1}".format(key, value))
                    valuefound = True
            if not valuefound:
                try:
                    print("{0} is triggered by {1}".format(layout.buttonmap[findkw], findkw))
                except KeyError:
                    pass

    elif len(view) > 0:
        if not view.startswith("layouts."):
            view2 = "layouts.{0}".format(view)
        else:
            view2 = view

        try:
            vl = layouts.load(view2)
            pprinter.pprint(vl.buttonmap)
        except ModuleNotFoundError as e:
            print("ERR: ModuleNotFoundError - error information below:")
            print(e)
    else:
        pprinter.pprint(layout.buttonmap)


commandmap = {
    "setlayout": setlayout,
    "listlayouts": listlayouts,
    "search": search,
    "commands": commands,
    "chooselayout": chooselayout,
    "viewlayout": viewlayout,
}
# End of functions for command mode

modemap = {
    "insert": "-- INSERT MODE (press enter to exit) --",
    "normal": "-- NORMAL MODE (press q to quit) --",
    "invalid": "-- INVALID MODE: Please report this error! --",
}

run = True  # Variable that says if the program should continue running
mode = "normal"  # Set the mode to normal (default)
layout = layouts.load("layouts.default")
host = input("Enter IP of the Roku you want to control: ")  # Ask for the IP of the Roku to control

while run:  # Main program loop
    if mode == "command":
        print("-- COMMAND MODE --")
        rawcmd = input(":")
        splitcmd = rawcmd.split(maxsplit=1)  # Split into two strings: the command, and the arguments
        if len(splitcmd) > 0:  # If a command was provided
            cmd = splitcmd[0]
        else:  # If no command was typed
            cmd = ""
        if len(splitcmd) > 1:  # If any arguments were provided
            args = splitcmd[1]
        else:  # If no arguments were provied
            args = ""

        if cmd == "q" or cmd == "quit":
            run = False  # Prevent the main program loop from executing again (ending the program)

        elif cmd in commandmap.keys():
            commandmap[cmd](args)

        else:
            print("ERR: Invalid command.")
        mode = "normal"

    else:
        print(modemap[mode])
        char = readchar.readkey()  # Read a single character
        print("Read: {0}".format(char))

        if mode == "insert":
            if char == "\r" or char == "\n":  # If enter was pressed
                mode = "normal"
            else:
                if len(char) == 1 and char.isalpha():
                    typechar = "LIT_" + char
                    libroku.sendbutton(pool, host, "keypress", typechar, on_error)
                else:
                    pchar = urllib.parse.quote(char)  # Percent encode the character (if needed)
                    print("ENCODED: '{0}'".format(pchar))
                    if pchar == "%7F" or pchar == "%08":
                        libroku.sendbutton(pool, host, "keypress", "Backspace", on_error)
                    else:
                        typechar = "LIT_" + pchar
                        libroku.sendbutton(pool, host, "keypress", typechar, on_error)

        elif mode == "normal":
            if char == "q":  # Quit command
                run = False  # Prevent the main program loop from running again

            elif char in layout.buttonmap.keys():  # If the character is in the dictionary of shortcuts
                libroku.sendbutton(pool, host, "keypress", layout.buttonmap[char], on_error)  # Press the button

            elif char == "i":  # Insert mode
                mode = "insert"

            elif char == ":":  # Command mode
                mode = "command"

            elif char == "/":  # Open Roku search menu
                libroku.sendbutton(pool, host, "search", "browse", on_error)  # Open the Roku search menu
