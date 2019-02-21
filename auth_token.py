#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" token.py -- Provides utility functions for exchanging an authorization
code for an access token, and for validating the access token.
"""
import json
import jwt
import requests
import textwrap
import urllib

from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

import constants
import auth_env


def get_access_token(code, env):
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
    """ Pulls jwks.json data from https://[YOUR_DOMAIN].auth0.com/.well-known/jwks.json
    """
    jwks = urllib.request.urlopen(env['tenant_url'] + '/.well-known/jwks.json')
    return json.loads(jwks.read())['keys'][0]


def extract_public_key(cert):
    """ Extracts the public key from the x.509 certificate taken from
    jwks.json.
    """
    cert_string = textwrap.wrap(cert, width=64)
    cert = '-----BEGIN CERTIFICATE-----\n'
    for line in cert_string:
        cert += line + '\n'
    cert += '-----END CERTIFICATE-----\n'
    cert_obj = load_pem_x509_certificate(cert.encode(), default_backend())
    return cert_obj.public_key()


def validate_token(token, env):
    """ Validate the access token.
    """
    jwks = get_jwks(env)
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
    """main -- if called directly, authenticate, get an authorization code,
    exchange the code for an access token, and validate the token.
    """
    import auth_env
    import login

    env = auth_env.load_env()
    code = login.authenticate(env)
    token = get_access_token(code, env)
    print(token)
    #print(validate_token(token, env))


if __name__ == '__main__':
    main()
