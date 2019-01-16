# QC QuickCheck

*Quick Check of Cisco CE endpoints info*

---

**ToDo's:**

- [ ] Consider writing your README first.  Doing so helps you clarify your intent, focuses your project, and it is much more fun to write documentation at the beginning of a project than at the end of one, see:
    - [Readme Driven Development](http://tom.preston-werner.com/2010/08/23/readme-driven-development.html)
    - [GitHub Guides: Mastering Markdown](https://guides.github.com/features/mastering-markdown/)
- [ ] Ensure you put the [license and copyright header](./HEADER) at the top of all your source code files.
- [ ] Be mindful of the third-party materials you use and ensure you follow Cisco's policies for creating and sharing Cisco Sample Code.

---

## Motivation

Include a short description of the motivation behind the creation and maintenance of the project.  Explain **why** the project exists.

## Show Me!

What visual, if shown, clearly articulates the impact of what you have created?  In as concise a visualization as possible (code sample, CLI output, animated GIF, or screenshot) show what your project makes possible.

## Features

Include a succinct summary of the features/capabilities of your project.

- Feature 1
- Feature 2
- Feature 3

## Technologies & Frameworks Used

This is Cisco Sample Code!  What Cisco and third-party technologies are you working with?  Are you using a coding framework or software stack?  A simple list will set the context for your project.

**Cisco Products & Services:**

- Product
- Service

**Third-Party Products & Services:**

- Product
- Service

**Tools & Frameworks:**

- Framework 1
- Automation Tool 2

## Usage

If people like your project, they will want to use it.  Show them how.

## Installation

Provide a step-by-step series of examples and explanations for how to install your project and its dependencies.
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


## Authors & Maintainers

Smart people responsible for the creation and maintenance of this project:

- Keller McBride <kelmcbri@cisco.com>

## Credits

Give proper credit.  Inspired by another project or article?  Was your work made easier by a tutorial?  Include links to the people, projects, and resources that were influential in the creation of this project.

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
