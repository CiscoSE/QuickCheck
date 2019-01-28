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

from json import loads,dumps
import cgi
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import http.client
import urllib.request
import logging
import ssl
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xmltodict
from lxml import etree

# Constants and Variables
# HOST_NAME is the address on your laptop running HTTPServer, i.e. localhost
# PORT_NUMBER is the port running ngrok tunnel i.e. 10010
# BOT_BEARER is your Bot's Bearer Authentication
# BOT_EMAIL is your Bot's email address i.e. qc@webex.bot
# BOT_NAME is the case sensitive name you gave your Bot. i.e. QC

ngrok_tunnel = " "
ngrok_port = " "


# ***  Methods
def getConfig():
    """
    This method reads the ./config.json file into the params
      variable.  These are the endpoints that will be acted on whenever a
      the QuickCheck bot invokes an action.
    """
    global HOST_NAME, PORT_NUMBER, BOT_BEARER, BOT_EMAIL, BOT_NAME


    # read file
    print(" ")
    print("Loading params list from ./config.json file")
    with open('./config.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    params = loads(data)
    print(" HERE ARE THE PARAMS :"+dumps(params))
    print (" HOST NAME : "+params["HOST_NAME"])

    HOST_NAME = params["HOST_NAME"]
    PORT_NUMBER = int(params["PORT_NUMBER"])
    BOT_BEARER = params["BOT_BEARER"]
    BOT_EMAIL = params["BOT_EMAIL"]
    BOT_NAME = params["BOT_NAME"]

    return

def getMode(host,hostname,codec_username,codec_password):
    """
    There are differences in the xAPI calls for endpoints that are
    registered to the cloud vs those that are registered on-prem so
    this method determines if device is registered on-prem or cloud and
    returns the 'Mode' of CUCM or Webex
    """

    mode = ""

    url = 'https://{}/getxml?location=/Configuration/Provisioning'.format(host)

    # GET the Mode. Response must be converted from XML to string with xpath
    try:
        mode = getCodecXML(
                  host,
                  codec_username,
                  codec_password,
                  url
                ).xpath('//Configuration/Provisioning/Mode/text()')[0]
        msg = (time.asctime()
                +"    "
                +hostname
                +"  Mode is: "
                +mode)
        print(msg)
    except:
        msg = (time.asctime()
               +" E  Can't reach "+hostname
               +" at addr: "
               +host
               +" to determine Mode")
        print(msg)

    return mode

def getCodecXML(host,codec_username,codec_password,url):
    """
    Send (GET) messages - xAPI commands and requests to Cisco CE
    based codecs.
    """

    # NOT checking certificates for https traffic. If you don't put this
    #    command in, your gets will encounter security pop-ups
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    try:
        response = requests.get(
            url,
            verify=False,
            timeout=2,
            auth=(codec_username, codec_password)
            )
        xmlstr = response.content
        root = etree.fromstring(xmlstr)
        return root

    except:
        msg = (time.asctime()
              +" E  Can't reach host "
              +host
              +" to GET XML request"
              )
        print(msg)

    return

def postCodecXML(host,codec_username,codec_password,url,payload,headers):
    """
    This method used to POST messages - xAPI commands and requests to Cisco CE
    based codecs.
    """

    # NOT checking certificates for https traffic
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        response = requests.post(
                      url,
                      data=payload,
                      verify=False,
                      timeout=2,
                      headers=headers,
                      auth=(codec_username, codec_password)
                      )
        #print ("response String : "+response.text)
        xmlstr = response.text
        root = etree.fromstring(xmlstr)
        return root
    except:
        msg = (time.asctime()
              +" E  Can't reach host "
              +host
              +" to POST XML request"
              )
        print(msg)

    return

def intent(action, webhook):
    """
    This method is called by the local http server whenever an action is sent
    by the webex teams webhook - and performs appropriate operation on the
    Endpoints
    """
    intent = action

    # Iterate through all the endpoints in the endpoints list
    for x in endpoints["endpoint"]:
        host = x["ipv4addr"]
        codec_username = x["admin"]
        codec_password = x["password"]
        hostname = x["name"]
        hostLocation = x["location"]

        # Find out if endpoint is cloud or onprem registered
        mode = getMode(host,hostname,codec_username,codec_password)

        # Act on intent/Action

        if intent   == "getpeople":
            # If the unit is on-prem registered, use this API call
            if mode == "CUCM":
                url = 'https://{}/getxml?location=/Status/RoomAnalytics/PeopleCount/Current'.format(host)

                try:
                    response = getCodecXML(
                                      host,
                                      codec_username,
                                      codec_password,
                                      url
                                      ).xpath('///Status/RoomAnalytics/PeopleCount/Current/text()')[0]
                    if response == "-1":
                        msg = (time.asctime()
                               +"    "
                               +hostname
                               +" : **Not currently enabled** for PeopleCount"
                              )
                        print (msg)
                    else:
                        msg = (time.asctime()
                               +"    There are **currently "
                               +response
                               +" people** in room :"
                               +hostname
                              )
                        print (msg)

                except:
                    msg = (time.asctime()
                      +"    PeopleCount API **not available** on "
                      +hostname
                      +" Hardware"
                      )
                    print(msg)
            # If the unit is registered to the cloud use this API call
            elif ((mode == "Webex") or (mode == "Auto")):
                url = 'https://{}/getxml?location=/Status/RoomAnalytics/PeopleCount/Current'.format(host)

                try:
                    response = getCodecXML(
                                      host,
                                      codec_username,
                                      codec_password,
                                      url
                                      ).xpath('///Status/RoomAnalytics/PeopleCount/Current/text()')[0]
                    if response == "-1":
                        msg = (time.asctime()
                               +"    "
                               +hostname
                               +" : **Not currently enabled** for PeopleCount"
                              )
                        print (msg)
                    else:
                        msg = (time.asctime()
                               +"    There are **currently "
                               +response
                               +" people** in room :"
                               +hostname
                              )
                        print (msg)

                except:
                    msg = (time.asctime()
                      +" E  **Can't reach** "
                      +hostname
                      +" at addr: "
                      +host
                      +" to get people count"
                      )
                    print(msg)

        elif intent == "callstatus":
                url = 'https://{}/getxml?location=/Status/Call'.format(host)
                # If the unit is on a call, it will answer to this call
                try:
                    response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                    xml_dict = xmltodict.parse(response.content)
                    connected = xml_dict["Status"]["Call"]["Status"]
                    calledParty = xml_dict["Status"]["Call"]["DisplayName"]
                    callType = xml_dict["Status"]["Call"]["CallType"]
                    direction = xml_dict["Status"]["Call"]["Direction"]
                    duration = xml_dict["Status"]["Call"]["Duration"]
                    rcvRate = xml_dict["Status"]["Call"]["ReceiveCallRate"]
                    sendRate = xml_dict["Status"]["Call"]["TransmitCallRate"]

                    msg = (time.asctime()
                           +"\n    "
                           +hostname
                           +" has been on a "
                           +direction
                           +" "
                           +callType
                           +" call for "
                           +duration
                           +" seconds with "
                           +calledParty
                           +" currently TX "
                           +sendRate
                           +" bps and Rcv "
                           +rcvRate
                           +" bps"
                          )

                #If the unit is not on a call it will answer with this call
                except:
                    #Check to see if unit is even registered
                    if mode == "CUCM":
                        url = 'https://{}/getxml?location=/Status/SIP'.format(host)
                        try:
                            response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                            xml_dict = xmltodict.parse(response.content)
                            registered = xml_dict["Status"]["SIP"]["Registration"]["Status"]
                            if registered == "Registered":
                                msg = (time.asctime()
                                       +"   "
                                       +hostname
                                       +" is SIP registered but **not currently on a call**."
                                      )

                        except:
                            msg = (time.asctime()
                                   +" E  Can't reach "
                                   +hostname
                                   +" at addr: "
                                   +host
                                   +" to determine Call Status"
                                  )
                    elif ((mode == "Webex") or (mode == "Auto")):
                        url = 'https://{}/getxml?location=/Status/Provisioning/Status'.format(host)

                        try:
                            response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                            xmlstr = response.content
                            root = etree.fromstring(xmlstr)
                            status = root.xpath('//Status/Provisioning/Status/text()')[0]
                            msg = (time.asctime()
                                   +"    "
                                   +hostname
                                   +" is: "
                                   +status
                                   +" to: "
                                   +mode
                                   +" but **not currently on a call**."
                                  )
                        except:
                            msg = (time.asctime()
                                   +" E  Can't reach "
                                   +hostname
                                   +" at addr: "
                                   +host
                                   +" to determine Call Status"
                                  )
                print(msg)

        elif intent == "list":
            msg = (time.asctime()
                  +"\t"
                  +hostname
                  +" address: "
                  +host
                  +" Location: "
                  +hostLocation
                  +"\n"
                  )

        elif intent == "getdiags":
            diags=""
            url = 'https://{}/getxml?location=/Status/Diagnostics'.format(host)
            #reponse holds all the diags, must break out individual diags
            try:
                response = getCodecXML(host,codec_username,codec_password,url)
                #How many diagnostic items are there
                tablecont = response.xpath('//Status/Diagnostics/Message/Description/text()')
                tablelen = len(tablecont)
                # Case where there are no diags found
                if tablelen == 0:
                    msg = (time.asctime()
                          +" - Diagnostic Messages "
                          +hostname
                          +" at "
                          +hostLocation
                          +" are: No Alerts Found"
                          )
                    print(msg)
                else:
                # One or more diags were found
                    for x in range(0,tablelen):
                        x = int(x)
                        diags = diags+("\n\t"+response.xpath('//Status/Diagnostics/Message/Description/text()')[x])
                        msg = (time.asctime()+" - Diagnostic Messages "+hostname+" at "+hostLocation+" are:\n"+diags)
                        print(msg)
            except:
                # Can't reach the endpoint to query it
                msg = (time.asctime()
                      +" E  Can't reach "
                      +hostname
                      +" at addr: "
                      +host
                      +" to determine Diags.")

        elif intent == "getversion":
            # If the unit is on-prem registered, use this API call
            if mode == "CUCM":
                url = 'https://{}/getxml?location=/Status/Provisioning/Software/Current'.format(host)

                try:
                    response = getCodecXML(
                                      host,
                                      codec_username,
                                      codec_password,
                                      url
                                      ).xpath('//Status/Provisioning/Software/Current/VersionId/text()')[0]
                    msg = (time.asctime()
                           +"    "
                           +hostname
                           +"  is running : **"
                           +response
                           +"** code and registered to "
                           +mode
                          )
                    print(msg)
                except:
                    msg = (time.asctime()
                           +" E  Can't reach "
                           +hostname
                           +" at addr: "
                           +host
                           +" to get version"
                          )
                    print (msg)
            # If the unit is registered to the cloud use this API call
            elif ((mode == "Webex") or (mode == "Auto")):
                url = 'https://{}/getxml?location=/Status/SystemUnit/Software/DisplayName'.format(host)

                try:
                    response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                    xmlstr = response.content
                    root = etree.fromstring(xmlstr)
                    status = root.xpath('///Status/SystemUnit/Software/DisplayName/text()')[0]
                    msg = (time.asctime()
                           +"    "
                           +hostname
                           +"  is running : **"
                           +status
                           +"** code and registered to "
                           +mode
                          )
                    print (msg)
                except:
                    msg = (time.asctime()
                      +" E  Can't reach "
                      +hostname
                      +" at addr: "
                      +host
                      +" to determine Cloud Software Version"
                      )
                    print(msg)
            else:
                msg = (time.asctime()
                  +" E  Unknown Mode "
                  +mode
                  )
                print(msg)

        elif intent == "sipstatus":
            # If the unit is on-prem registered, use this API call
            if mode == "CUCM":
                url = 'https://{}/getxml?location=/Status/SIP/Registration'.format(host)

                try:
                    response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                    xmlstr = response.content
                    root = etree.fromstring(xmlstr)
                    status = root.xpath('//Status/SIP/Registration/Status/text()')[0]
                    msg = (time.asctime()
                           +"    "
                           +hostname
                           +" Sip Registration Status is: **"
                           +status
                           +" to: "
                           +mode
                           +"**"
                          )
                except:
                    msg = (time.asctime()
                      +" E  Can't reach "
                      +hostname
                      +" at addr: "
                      +host
                      +" to determine SIP Registration Status"
                      )
                    print(msg)
            # If the unit is registered to the cloud use this API call
            elif ((mode == "Webex") or (mode == "Auto")):
                url = 'https://{}/getxml?location=/Status/Provisioning/Status'.format(host)

                try:
                    response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                    xmlstr = response.content
                    root = etree.fromstring(xmlstr)
                    status = root.xpath('//Status/Provisioning/Status/text()')[0]
                    msg = (time.asctime()
                           +"    "
                           +hostname
                           +"  Cloud Registered Status is: **"
                           +status
                           +" to: "
                           +mode
                           +"**"
                          )
                except:
                    msg = (time.asctime()
                      +" E  Can't reach "
                      +hostname
                      +" at addr: "
                      +host
                      +" to determine Cloud Registration Status"
                      )
                    print(msg)

        elif intent == "getloss":
            url = 'https://{}/getxml?location=/Status/MediaChannels'.format(host)
            video = "No"
            audio = "No"
            try:
                response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
                xml_dict = xmltodict.parse(response.content)
                #print(xml_dict)
            except:
                video = "N/A"
                audio = "N/A"
                msg = (
                       time.asctime()
                       +" Loss Stats for "
                       +hostname
                       +"    Video Loss: "
                       +video
                       +"  Audio Loss: "
                       +audio
                      )
                return video, audio
            try:
                check = xml_dict["Status"]["MediaChannels"]
                if check != "None":
                    totalin = 0
                    totalout = 0
                    channels = xml_dict["Status"]["MediaChannels"]["Call"]["Channel"]
                    for channel in channels:
                        #print(channel)
                        if "Video" in channel.keys() and channel["Video"]["ChannelRole"] == "Main":
                            direction = channel["Direction"]
                            print("The DIRECTION is :"+direction)
                            if direction == "Incoming":
                                lossin = float(channel["Netstat"]["Loss"])
                                pksin = float(channel["Netstat"]["Packets"])
                                #print("lossin is : "+str(lossin))
                                if lossin == 0:
                                    totalin = 0
                                else:
                                    totalin = (lossin/pksin)* 100
                                if (totalin > 5):
                                    video = "Yes"
                            else:
                                try:
                                    lossout = float(channel["Netstat"]["Loss"])
                                    pksout = float(channel["Netstat"]["Packets"])

                                    if lossout == 0:
                                        totalout = 0
                                    else:
                                        totalout = (lossout / pksout) * 100
                                        if (totalout > 5):
                                            video = "Yes"
                                except:
                                    print("There wasn't a field for netstat")
                        print("\n\n Video IN : "+str(totalin)+" Video Out : "+str(totalout))

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
                                if lossout == 0:
                                    totalout = 0
                                else:
                                    totalout = (lossout/pksout)* 100
                                if (totalout > 5):
                                    audio = "Yes"
                        print("Channel "+channel+" Audio IN : "+totalin+" Audio Out : "+totalout)
                else:
                    audio = "N/A"
            except:
                audio = "N/A"
            msg = (
                   time.asctime()
                   +" Loss Stats for "
                   +hostname
                   +"    Video Loss: "
                   +video
                   +"  Audio Loss: "
                   +audio
                  )
            print(msg)

        elif intent == "getlast":
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

                msg = "Last Call Hostname: {}\n\tHost: {}\n\tRemote#: {}\n\tRemoteName: {}\n\tDirection: {}\n\tProtocol: {}\n\tCallType: {}\n\tSeconds: {}\n\tRequestedType: {}\n\tStart: {}\n\tEnd: {} ".format(hostname, host ,RemoteNumber,DisplayName,Direction,Protocol,CallType,Seconds,ReqCallType,StartTime,EndTime)

            except:
                msg = (time.asctime()
                       +"    Failed getting Last Call Info for "
                       +hostname
                       +" at "
                       +host
                       )

                print (msg)

        elif intent == "getnumber":
            """
            getNumber returns phone numbers of endpoint
            """
            url = 'https://{}/getxml?location=/Status/UserInterface/ContactInfo/ContactMethod'.format(host)
            number=""
            #reponse holds all the numbers, must break out individual numbers
            try:
                response = getCodecXML(host,codec_username,codec_password,url)
                #How many Numbers items are there
                tablecont = response.xpath('//Status/UserInterface/ContactInfo/ContactMethod/Number/text()')
                tablelen = len(tablecont)
                # Case where there are no Numbers are found
                if tablelen == 0:
                    msg = (time.asctime()
                          +" - Numbers "
                          +hostname
                          +" at "
                          +hostLocation
                          +" are: No Numbers Found"
                          )
                    print(msg)
                else:
                # One or more Numbers were found
                    for x in range(0,tablelen):
                        x = int(x)
                        number = number+("\n\t"+response.xpath('/Status/UserInterface/ContactInfo/ContactMethod/Number/text()')[x])
                        msg = (time.asctime()
                               +"    "
                               +hostname
                               +" at "
                               +hostLocation
                               +" can be reached at :\n"
                               +number
                              )
                        print(msg)
            except:
                # Can't reach the endpoint to query it
                msg = (time.asctime()
                      +" E  Can't reach "
                      +hostname
                      +" at addr: "
                      +host
                      +" to determine Numbers.")
                print(msg)

        else:
            msg = "\n\n**Welcome to QuickCheck**\n\n" \
                  "\n" \
                  "Here are the actions supported by QuickCheck:  \n" \
                  "  **help** - This help menu  \n" \
                  "  **list** - print endpoints from endpoints.json list.  \n" \
                  "  **callStatus** - Shows current call status.  \n" \
                  "  **getDiags** - List any diagnostic alerts.  \n" \
                  "  **getVersion** - List current software version.  \n" \
                  "  **sipStatus** - List SIP registration Status.  \n" \
                  "  **getLoss** - List Packet Loss values.  \n" \
                  "  **getLast** - List Last Call Details.  \n" \
                  "  **getPeople** - List number of people in room.  \n"\
                  "  **getNumber** - Get Endpoint Numbers.  \n"

            print (time.asctime(),
                     "      POSTing msg to Webex Teams      ->  "
                     +msg
                     )
            print (time.asctime(),
                     "      POSTing to teams space id       ->  "
                     +webhook['data']['roomId']
                     )
            #send to webex now instead of waiting till end of intent if
            # statements or it will run once for each endpoint.:)
            try:
                sendSparkPOST("https://api.ciscospark.com/v1/messages",
                             {
                              "roomId": webhook['data']['roomId'],
                              "markdown": msg
                             }
                             )
            except:
                print (time.asctime(),"      Failed sending to Webex   ->  ")
            #return now so we don't run for every endpoint
            return

        # Take MSG generated in one of above intents and send to webex teams
        try:
            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                          {
                           "roomId": webhook['data']['roomId'],
                           "markdown": msg
                          }
                         )
        except:
            print (time.asctime(),"      Failed sending to Webex   ->  ")

def loadEndpoints():
    """
    This method reads the ./endpoints.json file into the loadEndpoints
      variable.  These are the endpoints that will be acted on whenever a
      the QuickCheck bot invokes an action.
    """
    global endpoints
    # read file
    print(" ")
    print("Loading endpoints list from ./endpoints.json file")
    with open('./endpoints.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    endpoints = loads(data)

    # show values
    for x in endpoints["endpoint"]:
        print ("\n")
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
    #data = loads(res.read())
    data = loads(res.read())
    for x in data["tunnels"]:
        print("ngrok public_url     : "+x["public_url"])
        print("ngrok tunnel on port : "+x["config"]["addr"])
    ngrok_port = data["tunnels"][0]["config"]["addr"]
    ngrok_tunnel = data["tunnels"][0]["public_url"]
    return

def checkWebhook():
    """
    This module checks to see if a webhook is already in place with webex
    teams to send chat traffic from your bot to the http server in this
    main.py program.  The webhook actually points to a public address hosted
    by ngrok which tunnels the traffic to the local http server.
    """

    print(" ")
    print("Checking Webex Teams to see if webhook for your bot is enabled")
    conn = http.client.HTTPSConnection("api.ciscospark.com")
    payload = ""
    headers = {
        'Authorization': "Bearer "+BOT_BEARER,
        'cache-control': "no-cache"
        }
    conn.request("GET", "/v1/webhooks", payload, headers)
    res = conn.getresponse()
    data = loads(res.read())

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
    payload = dumps({"name":"QC Webhook","targetUrl":ngrok_tunnel})
    headers = {
    'Authorization': "Bearer "+BOT_BEARER,
    'Content-Type': "application/json",
    'cache-control': "no-cache"
    }
    try:
        conn.request("PUT", "/v1/webhooks/"+webhookId, payload, headers)

        res = conn.getresponse()
        data = loads(res.read())

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
    therequest.add_header("Authorization", "Bearer "+BOT_BEARER)
    contents = urllib.request.urlopen(therequest).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is altered code from https://developer.webex.com/blog/spark-bot-demo
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    therequest = urllib.request.Request(url,bytes(dumps(data),"utf8"))
    therequest.add_header("Authorization", "Bearer "+BOT_BEARER)
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
        self.wfile.write(bytes(dumps({'Response': 'A Msg to you', 'Details': 'You sent a GET not a Post'}),"utf8"))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        webhook = loads(self.rfile.read(length))
        result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
        result = loads(result)
        if "text" in result:
            print (time.asctime(),"   TXT received via Post from webhook <- ",result["text"])
        if "files" in result:
            print (time.asctime(),"   FileID received via Post from hook <- ",result["files"])
        print (time.asctime(),"      Received from email address     <- ",result["personEmail"])
        print (time.asctime(),"      Received from teams space id    <- ",result["roomId"])

        msg = None
        if webhook['data']['personEmail'] != BOT_EMAIL:
            #If the incoming message is not from BOT_EMAIL, then convert the
            # incoming message to lower case and strip out BOT_NAME
            bot_name_lower = BOT_NAME.lower()
            in_message = result.get('text', '').lower()

            in_message = in_message.replace(str(bot_name_lower), '')
            in_message = in_message.strip()

            # first word in message after bot name removed is now the action
            # to be acted on
            x = in_message.split(" ", -1)
            x = x[0]
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
 # Get configuration parameters from config.json file
    getConfig()

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
