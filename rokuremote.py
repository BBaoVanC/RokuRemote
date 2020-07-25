#!/usr/bin/env python3
"""
RokuRemote

by bbaovanc

Program to control a Roku using your computer
"""

# Imports
import urllib  # Used here for percent encoding
from multiprocessing.dummy import Pool  # Used for async requests

import readchar  # Library to read single characters of input
import requests  # Library to easily send HTTP requests
import time  # Used for pauses

pool = Pool(50)  # Create async task pool
host = input("Enter IP of the Roku you want to control: ")  # Ask for the IP of the Roku to control
buttonmap = {
    "h": "Left",
    "j": "Down",
    "k": "Up",
    "l": "Right",
    "n": "Select",
    "p": "InstantReplay",
    "o": "Info",
    "b": "Rev",
    "y": "Fwd",
    "g": "Play",
    "u": "Back",
    "m": "Home",
    "x": "Power",
    "8": "VolumeDown",
    "9": "VolumeUp",
    "0": "VolumeMute",
    ",": "ChannelDown",
    ".": "ChannelUp",
}

secretmap = {
    "menu1": "mmmmmyyybb",
    "menu2": "mmmmmkljhk",  # Doesn't work
    "wifi": "mmmmmkjkjk",  # Doesn't work
    "platform": "mmmmmygbgy",  # Doesn't work
    "antenna": "mmmmmyjbjy",  # Doesn't work
    "bitrate": "mmmmmbbbyy",  # Doesn't work
    "developer": "mmmkklhlhl",  # Doesn't work
    "channelinfo": "mmmkkhlhlh",
    "network": "mmmmmlhlhl",  # Doesn't work
    "reboot": "mmmmmkbbyy",  # Doesn't work
}


def on_error(error):  # Called when an error occurs in HTTP requests
    print("POST ERROR")
    print(error)


def sendseq(seq):
    if len(seq) > 0:  # Ensure there's a sequence to send
        print("Running sequence: {0}".format(seq))  # Inform user of the sequence being run
        for b in seq:
            if b in buttonmap.keys():  # Ensure the current button is in the dictionar of buttons
                bsend = buttonmap[b]  # Figure out the name of the button to press
                sendbutton("keypress", bsend)  # Press the button
                time.sleep(0.5)  # Wait a half second before sending the next button in the sequence


def sendbutton(action, button):
    pressurl = "http://{0}:8060/{1}/{2}".format(host, action, button)  # The url to POST to
    pool.apply_async(requests.post, args=(pressurl,),
                     error_callback=on_error)  # Asynchronously send the POST request
    print("Sent: {0}/{1}".format(action, button))  # Inform the user of the request that has just been sent


def sendsearch(rawquery):
    query = urllib.parse.quote(rawquery)  # Percent enccode any characters that need to be encoded
    searchurl = "http://{0}:8060/search/browse?keyword={1}".format(host, query)
    pool.apply_async(requests.post, args=(searchurl,),
                     error_callback=on_error)  # Asynchronously send the POST request
    print("Searching for: {0}".format(query))  # Inform the user of the request that has just been sent


run = True  # Variable that says if the program should continue running
mode = "normal"  # Set the mode to normal (default)
validlayouts = ["default"]  # List of valid keyboard shortcut layouts
layout = "default"  # Set the keyboard layout

while run:  # Main program loop
    if mode == "command":
        print("-- COMMAND MODE --")
        rawcmd = input(":")
        splitcmd = rawcmd.split(maxsplit=1)  # Split into two strings: the command, and the arguments
        if len(splitcmd) > 0:  # If a command was provided
            cmd = splitcmd[0]
        else:  # If no command was typed
            cmd = ""
        if len(splitcmd) > 0:  # If any arguments were provided
            args = splitcmd[1]
        else:  # If no arguments were provied
            args = []
        if cmd == "q" or cmd == "quit":
            run = False  # Prevent the main program loop from executing again (ending the program)
        if cmd == "layout":
            if len(args) > 0:  # If an argument was provided
                if args[0] in validlayouts:  # If the requested layout is valid
                    layout = args[0]  # Change layout
                    print("layout set to {0}".format(layout))
                else:
                    print("ERR: Invalid layout. Valid layouts: {0}".format(validlayouts))
                    print("Current layout: {0}".format(layout))
            else:
                print("ERR: Invalid layout. Valid layouts: {0}".format(validlayouts))
                print("Current layout: {0}".format(layout))

        elif cmd == "search":
            sendsearch(args)

        elif cmd == "norm":
            if len(args) > 0:
                sendseq(args)
            else:
                print("ERR: No normal mode sequence specified")

        elif cmd == "secret":
            if len(args) > 0:
                sendseq(secretmap[args])
            else:
                print("ERR: No secret menu specified. Valid menus: {0}".format(list(secretmap.keys())))

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
        char = readchar.readchar()  # Read a single character
        print("Read: {0}".format(char))

        if mode == "insert":
            if char == "\r" or char == "\n":  # If enter was pressed
                mode = "normal"
            elif char == "\x7f":  # If backspace was pressed
                sendbutton("keypress", "Backspace")
            else:
                if len(char) == 1 and char.isalpha():
                    typechar = "LIT_" + char
                    sendbutton("keypress", typechar)
                else:
                    pchar = urllib.parse.quote(char)  # Percent encode the character (if needed)
                    print("ENCODED: '{0}'".format(pchar))
                    typechar = "LIT_" + pchar
                    sendbutton("keypress", typechar)
        elif mode == "normal":
            if char == "q":  # Quit command
                run = False  # Prevent the main program loop from running again

            elif char in buttonmap.keys():  # If the character is in the dictionary of shortcuts
                sendbutton("keypress", buttonmap[char])  # Press the button

            elif char == "i":  # Insert mode
                mode = "insert"

            elif char == ":":  # Command mode
                mode = "command"

            elif char == "/":  # Open Roku search menu
                sendbutton("search", "browse")  # Open the Roku search menu
