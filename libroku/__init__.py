#!/usr/bin/env python3
"""
libroku

by bbaovanc

Library for interacting with Roku devices
"""

# Imports
import requests
import urllib


def sendbutton(pool, host, action, button, on_error):
    pressurl = "http://{0}:8060/{1}/{2}".format(host, action, button)  # The url to POST to
    pool.apply_async(requests.post, args=(pressurl,),
                     error_callback=on_error)
    print("Sent: {0}/{1}".format(action, button))  # Inform the user of the request that has just been sent


def sendsearch(pool, host, rawquery, on_error):
    query = urllib.parse.quote(rawquery)  # Percent enccode any characters that need to be encoded
    searchurl = "http://{0}:8060/search/browse?keyword={1}".format(host, query)
    pool.apply_async(requests.post, args=(searchurl,),
                     error_callback=on_error)
    print("Searching for: {0}".format(query))  # Inform the user of the request that has just been sent

