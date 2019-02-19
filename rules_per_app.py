#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""apps_and_rules.py -- Writes to stdout a CSV file mapping rules to
applications. Each line of the CSV represents a single application and
all the rules that apply to that application.
"""
import csv
import requests
import sys

from dotenv import load_dotenv
from os import environ as env
from pathlib import Path

import constants
import login


def main():
    """main"""
    cw = csv.writer(sys.stdout)

    env = login.load_env()
    login.authenticate(env)
    token = login.get_access_token(env)

    url = env['management_url'] + 'rules'
    headers = {'Authorization': 'Bearer %s' % token['access_token']}
    rules = requests.get(url, headers=headers).json()

    url = env['management_url'] + 'clients'
    headers = {'Authorization': 'Bearer %s' % token['access_token']}
    clients = requests.get(url, headers=headers).json()


    for client in clients:
        application = []
        application.append(client['name'])
        for rule in rules:
            application.append(rule['name'])
        cw.writerow(application)



if __name__ == '__main__':
    main()
