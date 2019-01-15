# QuickCheck
Quick way to check various settings on multiple Cisco Telepresence Codecs running CE code.


Pre-Requisites for QuickCheck
  - Create a webex teams bot - I created QC@webex.bot
      How to create a webex teams bot (using python):
  https://developer.webex.com/blog/spark-bot-demo
  - Invite your bot to a webex teams space
  - Create a webex teams webhook that will listen for messages to your bot and forward them to your bot handling app. (this app)
    HowTo:
  - Get an account on ngrok which gives you a tunnel from ngrok to your laptop and a public address at ngrok for your webhook to send http messages to.  *** ngrok is sometimes considered a security risk by corporate security services, so check with IT before loading ngrok client on your laptop.
    - Launch ngrok client on laptop
- Edit endpoints.json file to include endpoints you want to manage.
- Run main.py from terminal on laptop
    main.py will
      - launch local HTTP server on port 10010
        (You can change port number in main.py/global variables)
      - check your local ngrok client and get public uri
      - edit your webex teams webhook with current ngrok target
