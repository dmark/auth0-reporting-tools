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
import base64
import hashlib
import json
import jwt
import logging
import pprint
import requests
import secrets
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

import constants

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


def auth0_url_encode(byte_data):
    """ Safe encoding handles + and /, and also replace = with nothing
    """
    return base64.urlsafe_b64encode(byte_data).decode('utf-8').replace('=', '')


def generate_challenge(a_verifier):
    """
    """
    return auth0_url_encode(hashlib.sha256(a_verifier.encode()).digest())


def load_env():
    """ Loads common settings into the env object.
    """
    env = {
        'response_type': 'code',
        'grant_type': 'authorization_code',
        'scopes': 'profile openid email read:clients read:rules',
        'code_challenge_method': 'S256'
    }

    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    env['client_id'] = environ[constants.AUTH0_CLIENT_ID]
    env['tenant_domain'] = environ[constants.AUTH0_DOMAIN]
    env['audience'] = environ[constants.AUTH0_AUDIENCE]
    env['callback_url'] = environ[constants.AUTH0_CALLBACK_URL]

    env['tenant_url'] = 'https://%s' % env['tenant_domain']
    env['authorize_url'] = env['tenant_url'] + '/authorize?'

    env['verifier'] = auth0_url_encode(secrets.token_bytes(32))
    env['code_challenge'] = generate_challenge(env['verifier'])
    env['state'] = auth0_url_encode(secrets.token_bytes(32))

    return env


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


def get_access_token(env):
    """ Exchange the authorization code for an access token.
    """
    token_url = env['tenant_url'] + '/oauth/token'
    headers = {'Content-Type': 'application/json'}
    body = {
        'grant_type': env['grant_type'],
        'client_id': env['client_id'],
        'code_verifier': env['verifier'],
        'code': code,
        'audience': env['audience'],
        'redirect_uri': env['callback_url']
        }
    return requests.post(token_url, headers=headers,
                         data=json.dumps(body)).json()


def get_jwks(env):
    """ Pulls https://[YOUR_DOMAIN].auth0.com/.well-known/jwks.json
    """
    jwks = urllib.request.urlopen(env['tenant_url'] + '/.well-known/jwks.json')
    return json.loads(jwks.read())['keys'][0]


def extract_public_key(cert):
    """ Extracts the public key from the x.509 certificate taken from
    jwks.json. The certificate in jwks.json is a broken PEM format
    which we need to fix before extracting the key.
    """
    cert_string = textwrap.wrap(cert, width=64)
    cert = '-----BEGIN CERTIFICATE-----\n'
    for line in cert_string:
        cert += line + '\n'
    cert += '-----END CERTIFICATE-----\n'
    cert_obj = load_pem_x509_certificate(cert.encode(), default_backend())
    return cert_obj.public_key()


def validate_token(token, jwks, env):
    """ Validate the access token.
    """
    public_key = extract_public_key(jwks['x5c'][0])
    try:
        jwt.decode(token['access_token'],
                   public_key,
                   audience=env['audience'],
                   issuer=env['tenant_url'] + '/',
                   algorithms=['RS256'])
    except jwt.InvalidAudienceError:
        return 'error: invalid_audience'
    except jwt.InvalidIssuerError:
        return 'error: invalid_issuer'
    except jwt.InvalidIssuedAtError:
        return 'error: invalid_issued_at'
    except jwt.ExpiredSignatureError:
        return 'error: expired_signature'
    else:
        return jwt.decode(token['access_token'],
                          public_key,
                          audience=env['audience'],
                          algorithms=['RS256'])


def main():
    """main -- if this module is called directly, authenticate, acquire an
    access token, validate the token, and print the validated token to stdout.
    """
    env = load_env()
    authenticate(env)

    if env['state'] != received_state:
        print('Error: session replay or similar attack in progress.')
        exit(-1)

    if error_message:
        print("An error occurred:")
        print(error_message)
        exit(-1)

    jwks = get_jwks(env)
    token = get_access_token(env)

    print(validate_token(token, jwks, env))


if __name__ == '__main__':
    main()
