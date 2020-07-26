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
import time  # Used for pauses

import layouts
import libroku

pool = Pool(50)  # Create async task pool
host = input("Enter IP of the Roku you want to control: ")  # Ask for the IP of the Roku to control


def on_error(error):  # Called when an error occurs in HTTP requests
    print("POST ERROR")
    print(error)


run = True  # Variable that says if the program should continue running
mode = "normal"  # Set the mode to normal (default)
layout = layouts.load("layouts.default")

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
        elif cmd == "setlayout":
            if len(args) > 0:
                if not args.startswith("layouts."):
                    args2 = "layouts.{0}".format(args)
                else:
                    args2 = args
                try:
                    layout = layouts.load(args2)
                except ModuleNotFoundError as e:
                    print("ERR: ModuleNotFoundError - error information below:")
                    print(e)
            else:
                print("ERR: No layout specified.")
                print("Current layout: {0}".format(layout.name))
                print("List all layouts by typing :layouts")

        elif cmd == "layouts":
            print("Valid layouts: {0}".format(layouts.getlist()))
            print("Use :setlayout to change layouts.")

        elif cmd == "search":
            libroku.sendsearch(pool, host, args, on_error)

        elif cmd == "norm":
            if len(args) > 0:
                sendseq(args)
            else:
                print("ERR: No normal mode sequence specified")

        else:
            print("ERR: Invalid command.")
        mode = "normal"

    else:
        if mode == "insert":
            print("-- INSERT MODE (press enter to exit) --")
        elif mode == "normal":
            print("-- NORMAL MODE (press q to quit) --")
        else:
            print("-- INVALID MODE: Please report this error! --")
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
