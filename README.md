# QuickCheck
Quick way to check various settings on multiple Cisco Telepresence Codecs running CE code.

Project is just getting started... no real application yet
- Run main.py from terminal on laptop
    main.py will
      - read in action list from ./include/actions.json
      - launch local HTTP server on port 10010.
- Log in to Webex Teams and invite qc.webex.bot to a space
- Launch NGROK on laptop to receive webhooks from webex teams that will be sent to laptop on port 10010
- Create/Edit Webex Teams Webhook so it points to current ngrok url for your laptop



Jan 8th, 2019
qc.webex.bot has been created on Webex Teams and can be invited to a space.
How to create a webex teams bot (using python)
https://developer.webex.com/blog/spark-bot-demo
Action Items
  Automate ngroc creation
  automate webhook edit to point to new ngroc tunnel
