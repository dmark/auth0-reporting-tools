#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" env.py
"""
import base64
import hashlib
import secrets

from dotenv import load_dotenv
from os import environ
from pathlib import Path

import constants


def base64_url_encode(byte_data):
    """ Safe encoding handles + and /, and also replace = with nothing
    """
    return base64.urlsafe_b64encode(byte_data).decode('utf-8').replace('=', '')


def generate_challenge(a_verifier):
    """
    """
    return base64_url_encode(hashlib.sha256(a_verifier.encode()).digest())


def load_env():
    """ Loads common settings into the env object.
    """
    env = {}
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    env['client_id'] = environ[constants.AUTH0_CLIENT_ID]
    env['callback_url'] = environ[constants.AUTH0_CALLBACK_URL]
    env['tenant_domain'] = environ[constants.AUTH0_DOMAIN]
    env['audience'] = environ[constants.AUTH0_AUDIENCE]
    env['response_type'] = environ[constants.AUTH0_RESPONSE_TYPE]
    env['grant_type'] = environ[constants.AUTH0_GRANT_TYPE]
    env['scopes'] = environ[constants.AUTH0_SCOPES]
    env['code_challenge_method'] = environ[constants.AUTH0_CODE_CHALLENGE_METHOD]

    env['tenant_url'] = 'https://%s' % env['tenant_domain']
    env['authorize_url'] = env['tenant_url'] + '/authorize?'

    env['verifier'] = base64_url_encode(secrets.token_bytes(32))
    env['code_challenge'] = generate_challenge(env['verifier'])
    env['state'] = base64_url_encode(secrets.token_bytes(32))

    return env


def main():
    """main
    """
    print(load_env())


if __name__ == '__main__':
    main()
