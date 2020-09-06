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
import pprint  # Used for pretty printing of button map
import os

import layouts
import libroku

pool = Pool(50)  # Create async task pool
pprinter = pprint.PrettyPrinter(indent=4)  # Create pretty printer

if not os.path.isfile("defaultlayout.txt"):  # if default layout isn't set
    print("defaultlayout.txt not found! Creating...")
    with open("defaultlayout.txt", "w+") as f:  # open defaultlayout.txt
        f.write("layouts.default")  # set the default layout to layouts.default


def on_error(error):  # Called when an error occurs in HTTP requests
    print("POST ERROR")
    print(error)


# Functions for command mode
def setlayout(new):
    global layout  # we want to use the global variable layout (instead of local)
    if len(new) > 0:  # if a new layout was given
        if not new.startswith("layouts."):  # if it doesn't start with layouts.
            args2 = "layouts.{0}".format(new)  # add layouts. to the beginning
        else:
            args2 = new
        try:
            layout = layouts.load(args2)  # try to load the requested layout
        except ModuleNotFoundError as e:  # if the layout doesn't exist
            print("ERR: ModuleNotFoundError - error information below:")
            print(e)  # print the ModuleNotFoundError

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
    laylist = layouts.getlist()  # get a list of valid layouts
    print("Type the number corresponding to the layout you want to use:")
    for a in range(len(laylist)):  # list out all the valid layouts
        print("[{0}] {1}".format(a, laylist[a]))

    sel = input("> ")  # ask which selection
    selint = int(sel)  # convert the selection to a number
    if selint in list(range(len(laylist))):  # if it was a valid selection number
        print("Selected: {0}".format(laylist[selint]))
        setlayout(laylist[selint])  # change the layout
    else:
        print("Invalid selection.")


def viewlayout(view):
    global layout  # use the global variable "layout"
    splitarg = view.split()  # convert arguments to a list
    valuefound = False  # obviously, we haven't found a match yet
    if len(splitarg) > 1:  # if more than one argument was given
        if splitarg[0] == "find":  # if the first argument is 'find'
            findkw = splitarg[1]  # the argument after find
            for key, value in layout.buttonmap.items():  # for all the keys in the buttonmap
                if value.lower() == findkw.lower():  # if the value matches
                    print("{0} is bound to {1}".format(key, value))
                    valuefound = True  # we found a match!
            if not valuefound:  # if we weren't able to find a match
                try:
                    # try to find a match the other direction
                    print("{0} is triggered by {1}".format(layout.buttonmap[findkw], findkw))
                except KeyError:  # if a match wasn't found the other direction
                    pass

    elif len(view) > 0:  # if at least one argument was provided
        if not view.startswith("layouts."):
            view2 = "layouts.{0}".format(view)  # add layouts. to beginning
        else:
            view2 = view

        try:
            vl = layouts.load(view2)  # load the requested layout
            pprinter.pprint(vl.buttonmap)  # pretty print the layout buttonmap
        except ModuleNotFoundError as e:  # if the layout wasn't found
            print("ERR: ModuleNotFoundError - error information below:")
            print(e)  # print the ModuleNotFoundError
    else:  # if no arguments were provided
        pprinter.pprint(layout.buttonmap)  # pretty print the current layout's buttonmap


def setdefaultlayout(arg=None):
    global layout  # use the global variable layout
    with open("defaultlayout.txt", "w") as f:
        f.write("layouts.{0}".format(layout.name))  # save the default layout
    print("Default layout set to {0}".format(layout.name))


commandmap = {
    "setlayout": setlayout,
    "listlayouts": listlayouts,
    "search": search,
    "commands": commands,
    "chooselayout": chooselayout,
    "viewlayout": viewlayout,
    "setdefaultlayout": setdefaultlayout,
}
# End of functions for command mode

modemap = {
    "insert": "-- INSERT MODE (press enter to exit) --",
    "normal": "-- NORMAL MODE (press q to quit) --",
    "invalid": "-- INVALID MODE: Please report this error! --",
}

run = True  # Variable that says if the program should continue running
mode = "normal"  # Set the mode to normal (default)
with open("defaultlayout.txt", "r") as f:
    deflayname = f.readlines()[0].strip()  # name of default layout
    print("Loading default layout: {0}".format(deflayname))
    layout = layouts.load(deflayname)  # load the default layout
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

        elif cmd in commandmap.keys():  # if it's a valid command
            commandmap[cmd](args)  # pass the arguments to that command

        else:
            print("ERR: Invalid command.")
        mode = "normal"

    else:
        print(modemap[mode])  # show the current mode
        char = readchar.readkey()  # Read a single character
        print("Read: {0}".format(char))

        if mode == "insert":
            if char == "\r" or char == "\n":  # If enter was pressed
                mode = "normal"
            else:
                if len(char) == 1 and char.isalpha():  # if a letter was pressed
                    typechar = "LIT_" + char
                    libroku.sendbutton(pool, host, "keypress", typechar, on_error)  # type the letter
                else:
                    pchar = urllib.parse.quote(char)  # Percent encode the character (if needed)
                    print("ENCODED: '{0}'".format(pchar))
                    if pchar == "%7F" or pchar == "%08":  # backspace key
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
