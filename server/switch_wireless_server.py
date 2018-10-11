#!/bin/env python

# Author: Frank Meier                                                             #
#                                                                                 #
# The purpose of this Script is to provide an easy way to turn RF on/off remotely #
# on a GNU/Linux system with the GNU coreutils installed                          #
# Just send a GET request of the following format:                                #
#                                                                                 #
# GET /?action=<ACTION> HTTP/1.1                                                  #
#                                                                                 #
# ACTION can be either "on", "off" or "toggle"                                    #


import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import devnull
from urllib import parse

# Pleas specify the desired port
PORT = 31415
ACCEPTED_ACTIONS = ["off", "on", "toggle"]
DEVNULL = open(devnull, 'w')


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = parse.urlparse(self.path)
            params = parse.parse_qs(parsed.query)
            action = params['action'][0].lower()

            if action in ACCEPTED_ACTIONS:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(switch(action).encode('utf-8'))
            else:
                error_message = 'Unknown parameter value for "action": ' + params['action'][0]
                self.send_error(400, error_message)
                print(error_message)
            return
        except:
            print(sys.exc_info())


# Rfkill offers a kernel interface to disable all wireless communication devices to save power
# This is prominently used by desktop environments like gnome for their "airplane mode"
# This ensures that all wireless devices are really powered off including bluetooth, wifi etc.

def switch(command):
    # Turn on/off /toggle all wireless communication via rfkill
    if command == 'toggle':
        ret = subprocess.call("rfkill "
                              "| grep blocked "
                              "| awk '{($4==\"unblocked\") ? system(\"rfkill block \" $1) "
                              ": system(\"rfkill unblock \" $1)}'", shell=True)

    elif command == 'on':
        ret = subprocess.call("rfkill list "
                              "| grep '^[0-9]' "
                              "| sed 's/:.*$//g' "
                              "| xargs rfkill unblock", shell=True)

    else:
        ret = subprocess.call("rfkill list "
                              "| grep '^[0-9]' "
                              "| sed 's/:.*$//g' "
                              "| xargs rfkill block", shell=True, stdout=DEVNULL, stderr=DEVNULL)

    status = subprocess.check_output("rfkill "
                                     "| grep -v '^ID' "
                                     "| awk '{ print $2 \" \" $4}' ", shell=True).decode('utf-8')
    print(status)

    return status


try:
    # Start Webserver in and turn wireless off first
    switch("off")
    server = HTTPServer(('0.0.0.0', PORT), GetHandler)
    print('starting wireless switching server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()
