#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" login.py -- provides user authentication for command line tools using
authorization code grant flow with PKCE. Opens a tab in your browser pointing
to your tenant's Universal Login page, and starts a web server locally to
receive the callback. The server is shut down once the callback has been
received and the authorization code recorded. The code is then exchanged for an
access token.

Based on: https://github.com/gateley-auth0/CLI-PKCE
"""
import json
import jwt
import logging
import pprint
import requests
import textwrap
import threading
import urllib
import webbrowser

from dotenv import load_dotenv
from os import environ
from pathlib import Path
from time import sleep
from werkzeug.serving import make_server

from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from flask import Flask
from flask import request

import auth_env
import auth_token

app = Flask(__name__)

# Silences logging from the temporary webserver
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Is there some way to get rid of these globals?
received_callback = False
code = None
error_message = None
received_state = None


@app.route('/callback')
def callback():
    """ The callback is invoked after a completed login attempt (succesful or
    otherwise). It sets global variables with the auth code or error messages,
    then sets the polling flag received_callback.
    """
    global received_callback, code, error_message, received_state
    if 'error' in request.args:
        error_message = request.args['error'] + ': ' \
            + request.args['error_description']
    else:
        code = request.args['code']
    received_state = request.args['state']
    received_callback = True
    return "You can close this window/tab and return to the command line."


class ServerThread(threading.Thread):
    """ The Flask server is done this way to allow shutting down after a single
    request has been received. A server is created only to receive the callback
    after the login attempt.
    """
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 3000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def authenticate(env):
    """ Opens a browser tab to the authentication url (Universal Login page of
    the configured tenant) and starts a server to receive the callback after
    the user logs in. The callback results in the global 'code' variable being
    populated with the authorization code, or the global error_message variable
    being populated if there was an error during authentication.
    """
    url_parameters = {
        'audience': env['audience'],
        'scope': env['scopes'],
        'response_type': env['response_type'],
        'redirect_uri': env['callback_url'],
        'client_id': env['client_id'],
        'code_challenge': env['code_challenge'].replace('=', ''),
        'code_challenge_method': env['code_challenge_method'],
        'state': env['state']
    }

    authentication_url = env['authorize_url'] + \
        urllib.parse.urlencode(url_parameters)

    webbrowser.open_new(authentication_url)
    server = ServerThread(app)
    server.start()
    while not received_callback:
        sleep(1)
    server.shutdown()

    return code


def main():
    """main -- if this module is called directly, authenticate, acquire an
    access token, validate the token, and print the validated token to stdout.
    """
    env = auth_env.load_env()
    authenticate(env)

    if env['state'] != received_state:
        print('Error: session replay or similar attack in progress.')
        exit(-1)

    if error_message:
        print("An error occurred:")
        print(error_message)
        exit(-1)

    token = auth_token.get_access_token(code, env)

    print(auth_token.validate_token(token, env))


if __name__ == '__main__':
    main()
