#!/usr/bin/env python3
#Document this file

# Imports

import json
import cgi
from http.server import BaseHTTPRequestHandler
import time
from http.server import HTTPServer
#from include.server import Server
import urllib.request
import urllib.parse
import urllib



# Constants and Variables
HOST_NAME = 'localhost'
PORT_NUMBER = 10010
bat_signal  = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
bearer = "ZmNmYzUxYWYtMzc2My00NTMzLTg1MzYtYWQxZmQ2M2Q1Nzc5YTAyZWMzNzctNjZj_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_email = "qc@webex.bot"
bot_name = "QC"

#Functions

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    therequest = urllib.request.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    therequest.add_header("Authorization", "Bearer "+bearer)
    contents = urllib.request.urlopen(therequest).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    therequest = urllib.request.Request(url,bytes(json.dumps(data),"utf8"))
    therequest.add_header("Authorization", "Bearer "+bearer)
    therequest.add_header("Accept", "application/json")
    therequest.add_header("Content-Type", "application/json")

    contents = urllib.request.urlopen(therequest).read()
    return contents

'''
 When a request comes in, the BaseHTTPRequestHandler will automatically route
  the request to the appropriate request method (either do_GET, do_HEAD or
  do_POST) which we’ve defined on our subclass
 We’ll use handle_http to send our basic http handlers and then return the content.
 - respond will be in charge of sending the actual response out

 The flow of data will look like this when a request is received:
   do_* receives request > respond invoked > handle_http bootstraps request,
   returns content > respond sends the response
'''

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(bytes(json.dumps({'Response': 'A Msg to you', 'Details': 'You sent a GET not a Post'}),"utf8"))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        webhook = json.loads(self.rfile.read(length))

        print ("This is the received data from post",webhook)
        print (webhook['data']['id'])
        result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
        result = json.loads(result)
        msg = None
        if webhook['data']['personEmail'] != bot_email:
            in_message = result.get('text', '').lower()
            in_message = in_message.replace(bot_name, '')
            if 'batman' in in_message or "whoareyou" in in_message:
                msg = "I'm Batman!"
                print(msg)
            elif 'batcave' in in_message:
                message = result.get('text').split('batcave')[1].strip(" ")
                if len(message) > 0:
                    msg = "The Batcave echoes, '{0}'".format(message)
                else:
                    msg = "The Batcave is silent..."
            elif 'batsignal' in in_message:
                    print ("NANA NANA NANA NANA")
                    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": bat_signal})
                    if msg != None:
                        print (msg)
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            return "true"


    def handle_http(self, status, content_type):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        return bytes('Hello World', 'UTF-8')

    def respond(self):
        content = self.handle_http(200, "text/html")
        self.wfile.write(content)

# Module Functions and Classes
def main():
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(" ")
    print("Use Ctrl-C to stop HTTP server")
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(" ")
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))

# Check to see if this file is the "__main__" script being executed
if __name__ == '__main__':
    main()
