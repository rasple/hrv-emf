#!/usr/bin/env python3

# Author: Frank Meier                                                             #
#                                                                                 #
# The purpose of this Script is to provide an easy way to turn RF on/off remotely #
# on a GNU/Linux system with the GNU coreutils installed                          #
# Just send a GET request of the following format:                                #
#                                                                                 #
# GET /?action=<ACTION> HTTP/1.1                                                  #
#                                                                                 #
# ACTION can be either "on", "off" or "toggle"                                    #


from http.server import BaseHTTPRequestHandler, HTTPServer
from os import devnull
from shutil import which
from subprocess import call, check_output
from sys import exc_info
from urllib import parse

# Please specify the desired port
PORT = 31415

DEVNULL = open(devnull, 'w')
ACCEPTED_ACTIONS = ["off", "on", "toggle", "status"]
REQUIRED_BINARIES = ['xargs', 'grep', 'rfkill', 'sed', 'awk']


# Check if required binaries are available
def check_bins(bins):
    for bin in bins:
        if not which(bin):
            print('Error: Dependency "' + bin + '" not found')
            print('Please check that "' + bin + '" is installed and in PATH')
            exit(-1)


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = parse.urlparse(self.path)
            params = parse.parse_qs(parsed.query)
            if 'action' in params:
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
            else:
                self.send_error(400, 'Please specify "action" parameter')
            return
        except:
            print(exc_info())


# Rfkill offers a kernel interface to disable all wireless communication devices to save power
# This is prominently used by desktop environments like gnome for their "airplane mode"
# This ensures that all wireless devices are really powered off including bluetooth, wifi etc.

def switch(command):
    # Turn on/off /toggle all wireless communication via rfkill
    if command == 'toggle':
        print(call("rfkill list "
                   "| grep blocked "
                   "| awk '{($4==\"unblocked\") ? system(\"rfkill block all \") "
                   ": system(\"rfkill unblock all \")}'", shell=True))

    elif command == 'on':
        print(call("rfkill unblock all && systemctl start hostapd.service", shell=True))

    else:
        # This command produces an error because when the first bluetooth device is deactivated the second one disappears
        # Since everything else works fine the output of the command has been muted
        print(call("rfkill block all && systemctl stop hostapd.service", shell=True))

    status = check_output("rfkill list", shell=True).decode('utf-8')
    print(status)

    return status


try:
    # Start Webserver in and turn wireless off first
    check_bins(REQUIRED_BINARIES)
    switch("off")
    server = HTTPServer(('0.0.0.0', PORT), GetHandler)
    print('starting wireless switching server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()
