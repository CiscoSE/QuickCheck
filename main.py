#!/usr/bin/env python3
"""
Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# Imports
import json
import cgi
from http.server import BaseHTTPRequestHandler
import time
from http.server import HTTPServer
import http.client
import urllib.request
import urllib.parse
import urllib
import os
import logging
import ssl
import requests
import xmltodict
from lxml import etree
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Constants and Variables
HOST_NAME = 'localhost'
PORT_NUMBER = 10010
bearer = "<<replace with Your Bots Bearer Token>>"
bot_email = "qc@webex.bot"
bot_name = "QC"
ngrok_auth_token = "<<replace with Your ngrok auth token>>"
ngrok_tunnel = " "
ngrok_port = " "
endpoints = " "
# ***  Methods

def getCodecXML(addr,user,passwd,msg):
    """
    Send (GET) messages - xAPI commands and requests to Cisco CE
    based codecs.
    """
    url = msg
    codec_username = user
    codec_password = passwd
    url = msg
    host = addr

    # NOT checking certificates for https traffic
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    try:
        response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
        xmlstr = response.content
        root = etree.fromstring(xmlstr)
        return root

    except:
        msg = (time.asctime()+" -  Can't reach host "+host)
        print(msg)

    return

def postCodecXML(host,user,passwd,url,payload,headers):
    """
    This method used to POST messages - xAPI commands and requests to Cisco CE
    based codecs.
    """
    codec_username = user
    codec_password = passwd
    url = url
    host = host
    payload = payload
    headers = headers

    # NOT checking certificates for https traffic
    try:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.post(url, data=payload, verify=False, timeout=2, headers=headers, auth=(codec_username, codec_password))
        #print ("response String : "+response.text)
        xmlstr = response.text
        root = etree.fromstring(xmlstr)
        return root
    except:
        msg = (time.asctime()+" -  Can't reach host "+host)
        print(msg)

    return

def intent(object, webhook):
    """
    This method is called by the local http server whenever an action is sent
    by the webex teams webhook - and performs appropriate operation on the
    Endpoints
    """
    intent = object


    print(time.asctime(),'   Intent received is ',intent)

    for x in endpoints["endpoint"]:
        host = x["ipv4addr"]
        codec_username = x["admin"]
        codec_password = x["password"]
        hostname = x["name"]
        hostLocation = x["location"]

        if intent ==   "help":
            msg = "Welcome to QuickCheck\n" \
                  "\n" \
                  "Here are the actions supported by QuickCheck:\n" \
                  "help - This help menu\n" \
                  "list - print endpoints from endpoints.json list.\n" \
                  "getStatus - Currently provides Standby Status.\n" \
                  "getDiags - List any diagnostic alerts. \n" \
                  "getVersion - List current software version.\n" \
                  "sipStatus - List SIP registration Status.\n" \
                  "getLoss - List Packet Loss values.\n" \
                  "getLast - List Last Call Details.\n" \
                  "getPeople - List number of people in room.\n"
            print (time.asctime(),"      POSTing msg to Webex Teams      ->  "+msg)
            print (time.asctime(),"      POSTing to teams space id       ->  "+webhook['data']['roomId'])
            try:
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            except:
                print (time.asctime(),"      Failed sending to Webex   ->  ")
            return

        elif intent == "getPeople":
            msg = (time.asctime()+"      Still coding getPeople method.")
            print(msg)
            try:
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            except:
                print (time.asctime(),"      Failed sending to Webex   ->  ")

            return

        elif intent == "getStatus":

            url = 'https://{}/getxml?location=/Status/Standby'.format(host)

            try:
                response = getCodecXML(host,codec_username,codec_password,url).xpath('//Status/Standby/State/text()')[0]
                msg = (time.asctime()+" - Standby status of "+hostname+" at "+hostLocation+" is: "+response)
                print(msg)
            except:
                msg = (time.asctime()+" -  Can't reach "+hostname+" at addr: "+host)

        elif intent == "list":
            msg = (time.asctime()+"\t"+hostname+" address: "+host+" Location: "+hostLocation+"\n")

        elif intent == "getDiags":
            diags=""
            url = 'https://{}/getxml?location=/Status/Diagnostics'.format(host)
            try:
                response = getCodecXML(host,codec_username,codec_password,url)
                tablecont = response.xpath('//Status/Diagnostics/Message/Description/text()')
                tablelen = len(tablecont)
                if tablelen == 0:
                    msg = (time.asctime()+" - Diagnostic Messages "+hostname+" at "+hostLocation+" are: No Alerts Found")
                    print(msg)
                else:
                    for x in range(0,tablelen):
                        x = int(x)
                        diags = diags+("\n\t"+response.xpath('//Status/Diagnostics/Message/Description/text()')[x])
                        msg = (time.asctime()+" - Diagnostic Messages "+hostname+" at "+hostLocation+" are:"+diags)
                        print(msg)
            except:
                msg = (time.asctime()+" -  Can't reach "+hostname+" at addr: "+host)

        elif intent == "getVersion":

            url = 'https://{}/getxml?location=/Status/Provisioning/Software/Current'.format(host)

            try:
                response = getCodecXML(host,codec_username,codec_password,url).xpath('//Status/Provisioning/Software/Current/VersionId/text()')[0]
                msg = (time.asctime()+" - CE Version running on "+hostname+" at "+hostLocation+" is:\n\t "+response)
                print(msg)
            except:
                msg = (time.asctime()+" -  Can't reach "+hostname+" at addr: "+host)

        elif intent == "sipStatus":
            msg = (time.asctime()+"      Still coding sipStatus method.")
            print(msg)
            try:
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            except:
                print (time.asctime(),"      Failed sending to Webex   ->  ")
            return

            url = 'https://{}/getxml?location=/Status/SIP/Registration'.format(host)
            #try:
            response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
            xmlstr = response.content
            root = etree.fromstring(xmlstr)
            print(etree.tostring(root, encoding="UTF-8"))
            status = root.xpath('//Status/SIP/Registration/Status/text()')[0]
            msg = ("Host Sip Registration Status is: "+status)
            print(time.asctime(),"      Received SIP Registration Stat  <- ",status)
            print (time.asctime(),"      POSTing msg to Webex Teams      ->  "+status)
            print (time.asctime(),"      POSTing to teams space id       ->  "+webhook['data']['roomId'])
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            #except:
            #    msg = (time.asctime()+" -  Can't reach "+hostname+" at addr: "+host)
            #    print(msg)
            #    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})

        elif intent == "getLoss":
            url = 'https://{}/getxml?location=/Status/MediaChannels'.format(host)
            video = "No"
            audio = "No"
            msg = (time.asctime()+"      Still coding getLoss method.")
            print(msg)
            try:
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            except:
                print (time.asctime(),"      Failed sending to Webex   ->  ")
            return
            try:
                response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                xml_dict = xmltodict.parse(response.content)
            except:
                video = "N/A"
                audio = "N/A"
                return video, audio
            try:
                check = xml_dict["Status"]["MediaChannels"]
                if check != "None":
                    channels = xml_dict["Status"]["MediaChannels"]["Call"]["Channel"]
                    for channel in channels:
                        if "Video" in channel.keys() and channel["Video"]["ChannelRole"] == "Main":
                            direction = channel["Direction"]
                            if direction == "Incoming":
                                lossin = float(channel["Netstat"]["Loss"])
                                pksin = float(channel["Netstat"]["Packets"])

                                if lossin == 0:
                                    totalin = 0
                                else:
                                    totalin = (lossin/pksin)* 100
                                if (totalin > 5):
                                    video = "Yes"
                            else:
                                lossout = float(channel["Netstat"]["Loss"])
                                pksout = float(channel["Netstat"]["Packets"])

                                if lossout == 0:
                                    totalout = 0
                                else:
                                    totalout = (lossout / pksout) * 100
                                if (totalout > 5):
                                    video = "Yes"
                else:
                    video = "N/A"
            except:
                video = "N/A"
            try:
                check = xml_dict["Status"]["MediaChannels"]
                if check != "None":
                    channels = xml_dict["Status"]["MediaChannels"]["Call"]["Channel"]
                    for channel in channels:
                        if "Audio" in channel.keys() and channel["Type"] == "Audio":
                            direction = channel["Direction"]
                            if direction == "Incoming":
                                lossin = float(channel["Netstat"]["Loss"])
                                pksin = float(channel["Netstat"]["Packets"])

                                if lossin == 0:
                                    totalin = 0
                                else:
                                    totalin = (lossin/pksin)* 100
                                if (totalin > 5):
                                    audio = "Yes"
                            else:
                                lossout = float(channel["Netstat"]["Loss"])
                                pksout = float(channel["Netstat"]["Packets"])
                                if lossout == 0:                                        totalout = 0
                                else:
                                    totalout = (lossout/pksout)* 100
                                if (totalout > 5):
                                    audio = "Yes"
                else:
                    audio = "N/A"
            except:
                audio = "N/A"
            print(video,"   ",audio)
            print(msg)

        elif intent == "getLast":
            """
            getLast gives stats on last call

            """

            url = 'https://{}/putxml'.format(host)
            payload = '<Command><CallHistory><Recents><DetailLevel>Full</DetailLevel><Limit>1</Limit></Recents></CallHistory></Command>'
            headers = {'Content-Type': 'text/xml'}

            try:
                root = postCodecXML(host,codec_username,codec_password,url,payload,headers)
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/RemoteNumber')[0]
                RemoteNumber = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/DisplayName')[0]
                DisplayName = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/Direction')[0]
                Direction = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/Protocol')[0]
                Protocol = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/CallType')[0]
                CallType = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/LastOccurrenceDuration')[0]
                Seconds = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/LastOccurrenceRequestedCallType')[0]
                ReqCallType = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/LastOccurrenceStartTime')[0]
                StartTime = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/LastOccurrenceEndTime')[0]
                EndTime = infoXML.text
                infoXML = root.xpath('//Command/CallHistoryRecentsResult/Entry/LastOccurrenceEndTime')[0]

                msg = "Last Call Hostname: {}\n\t Host: {}\n\tRemote#: {}\n\tRemoteName: {}\n\tDirection: {}\n\tProtocol: {}\n\tCallType: {}\n\tSeconds: {}\n\tRequestedType: {}\n\tStart: {}\n\tEnd: {} ".format(hostname, host ,RemoteNumber,DisplayName,Direction,Protocol,CallType,Seconds,ReqCallType,StartTime,EndTime)

            except:
                msg = ("Failed getting Last Call Info for "+hostname+" at "+host)
                print (msg)

        else:
            msg = "I don't know that action"
            print(msg)

        print (time.asctime(),"      POSTing msg to Webex Teams      ->  "+msg)
        print (time.asctime(),"      POSTing to teams space id       ->  "+webhook['data']['roomId'])
        try:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        except:
            print (time.asctime(),"      Failed sending to Webex   ->  ")
    return

def loadEndpoints():
    """
    This method reads the ./include/endpoints.json file into the loadEndpoints
      variable.  These are the endpoints that will be acted on whenever a
      the QuickCheck bot invokes an action.
    """
    global endpoints
    # read file
    print(" ")
    print("Loading endpoints list from ./include/endpoints.json file")
    with open('./endpoints.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    endpoints = json.loads(data)

    # show values
    for x in endpoints["endpoint"]:
        print ("Name          : "+x["name"])
        print ("Location      : "+x["location"])
        print ("IP v4 Address : "+x["ipv4addr"])
        print ("Type          : "+x["type"])
    return

def checkNgrok():
    """
    This module checks to see that ngrok is running on the localhost
    and a tunnel is configured to reach public url.
    """
    global ngrok_tunnel

    # Checking for local http server on 4040 which is standard ngrok service
    print(" ")
    print("Checking ngrok to see if ngroc tunnel is active.")
    print("Current active ngrok tunnels running on laptop are:")
    conn = http.client.HTTPConnection("localhost:4040")
    payload = ""
    headers = { 'cache-control': "no-cache" }
    conn.request("GET", "/api/tunnels", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    for x in data["tunnels"]:
        print("ngrok public_url     : "+x["public_url"])
        print("ngrok tunnel on port : "+x["config"]["addr"])
    ngrok_port = data["tunnels"][0]["config"]["addr"]
    ngrok_tunnel = data["tunnels"][0]["public_url"]
    return

def checkWebhook():
    """
    This module checks to see if a webhook is already in place with webex
    teams to send chat traffic from qc.webex.bot to the http server in this
    main.py program.  The webhook actually points to a public address hosted
    by ngrok which tunnels the traffic to the local http server.
    """

    print(" ")
    print("Checking Webex Teams to see if webhook for qc.webex.bot is enabled")
    conn = http.client.HTTPSConnection("api.ciscospark.com")
    payload = ""
    headers = {
        'Authorization': "Bearer "+bearer,
        'cache-control': "no-cache"
        }
    conn.request("GET", "/v1/webhooks", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())

    for x in data["items"]:
        print("Webex Teams Webhook Name: "+x["name"])
        print("The Webex Teams Webhook Target URL is : "+x["targetUrl"])
        print("Webhook ID: "+x["id"])
    current_tunnel = data["items"][0]["targetUrl"]
    webhookId = data["items"][0]["id"]
    # print(data["items"][0])
    print(" ")


    print("Updating webex teams Webhook target url with current ngrok tunnel")
    conn = http.client.HTTPSConnection("api.ciscospark.com")
    payload = json.dumps({"name":"QC Webhook","targetUrl":ngrok_tunnel})
    headers = {
    'Authorization': "Bearer "+bearer,
    'Content-Type': "application/json",
    'cache-control': "no-cache"
    }
    try:
        conn.request("PUT", "/v1/webhooks/"+webhookId, payload, headers)

        res = conn.getresponse()
        data = json.loads(res.read())

        print("Webex Teams Webhook updated:")
        print("Webhook name       : "+data["name"])
        print("Webhook Target URL : "+data["targetUrl"])
    except:
        print("Couldn't PUT to set webhook")
    return

def sendSparkGET(url):
    """
    This method is altered code from https://developer.webex.com/blog/spark-bot-demo
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
    This method is altered code from https://developer.webex.com/blog/spark-bot-demo
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    therequest = urllib.request.Request(url,bytes(json.dumps(data),"utf8"))
    therequest.add_header("Authorization", "Bearer "+bearer)
    therequest.add_header("Accept", "application/json")
    therequest.add_header("Content-Type", "application/json")

    contents = urllib.request.urlopen(therequest).read()
    return contents

class Server(BaseHTTPRequestHandler):
    '''
    This class is -VERY- altered code from https://developer.webex.com/blog/spark-bot-demo
    When a request comes in, the BaseHTTPRequestHandler will automatically route
    the request to the appropriate request method (either do_GET, do_HEAD or
    do_POST) which we’ve defined on our subclass
    We’ll use handle_http to send our basic http handlers and then return the content.
        - respond will be in charge of sending the actual response out

    The flow of data will look like this when a request is received:
    do_* receives request > respond invoked > handle_http bootstraps request,
    returns content > respond sends the response
    '''
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        # GET sends back a Hello world message
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
        #print (webhook['data']['id'])
        result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
        result = json.loads(result)
        if "text" in result:
            print (time.asctime(),"   TXT received via Post from webhook <- ",result["text"])
        if "files" in result:
            print (time.asctime(),"   FileID received via Post from hook <- ",result["files"])
        print (time.asctime(),"      Received from email address     <- ",result["personEmail"])
        print (time.asctime(),"      Received from teams space id    <- ",result["roomId"])

        msg = None
        if webhook['data']['personEmail'] != bot_email:
            #in_message = result.get('text', '').lower()
            in_message = result.get('text', '')
            #in_message = in_message.replace(bot_name, '')
            # first word in message is the action
            x = in_message.split(" ", 1)
            x = x[1]
            intent(x, webhook)
            return "true"


    def handle_http(self, status, content_type):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        return bytes('Hello World', 'UTF-8')

    def respond(self):
        content = self.handle_http(200, "text/html")
        self.wfile.write(content)

def main():
 # Turn on logging
    logger = logging.getLogger(__name__)
 # Check on ngrok tunnels
    checkNgrok()
 # Check on Webex Teams webhook
    checkWebhook()

 # Read in the endpoints list from endpoints.json files
    loadEndpoints()

 # Initialize HTTP server to receive webhooks from Webex Teams and Push
 #   QuickCheck Bot responses back to webex teamsself.
 #   The web service will run until you hit control c to stop it.
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(" ")
    print("Starting local HTTP server")
    print("Use Ctrl-C to stop HTTP server")
    print(time.asctime(), '   Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
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
