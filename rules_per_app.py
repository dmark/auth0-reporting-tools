#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""apps_and_rules.py -- Writes to stdout a CSV file mapping rules to
applications. Each line of the CSV represents a single application and
all the rules that apply to that application.
"""
import csv
import pprint
import re
import requests
import sys

from dotenv import load_dotenv
from os import environ as env
from pathlib import Path

import constants
import login


def main():
    """main"""

    env = login.load_env()
    login.authenticate(env)
    token = login.get_access_token(env)

    url = env['audience'] + 'rules'
    headers = {'Authorization': 'Bearer %s' % token['access_token']}
    rules = requests.get(url, headers=headers).json()

    url = env['audience'] + 'clients'
    headers = {'Authorization': 'Bearer %s' % token['access_token']}
    clients = requests.get(url, headers=headers).json()
    applications = {}
    # Create a dictionary of lists, with client names as the keys
    for client in clients:
        if client['name'] == "All Applications":
            continue
        applications[client['name']] = []

    for rule in rules:
        # Skip rules that are disabled
        if rule['enabled'] is False:
            continue

        s_clientName_equal = '.*context.clientName ===.*'
        s_clientName_notequal = '.*context.clientName !==.*'

        if re.search(s_clientName_equal, rule['script'], re.M | re.I):
            # Rule has "context.clientName ===", add to matching clients
            for client in clients:
                if client['name'] == "All Applications":
                    continue
                s_string = '.*context.clientName === \'' + \
                    client['name'] + '\'.*'
                if re.search(s_string, rule['script'], re.M | re.I):
                    applications[client['name']].append(rule['name'])
                else:
                    applications[client['name']].append('')
        elif re.search(s_clientName_notequal, rule['script'], re.M | re.I):
            # Rule has "context.clientName !==", add to non-matching clients
            for client in clients:
                if client['name'] == "All Applications":
                    continue
                s_string = '.*context.clientName !== \'' + \
                    client['name'] + '\'.*'
                if re.search(s_string, rule['script'], re.M | re.I):
                    applications[client['name']].append('')
                else:
                    applications[client['name']].append(rule['name'])
        else:
            # Rule has no context.clientName, applies to all clients
            for client in clients:
                if client['name'] == "All Applications":
                    continue
                applications[client['name']].append(rule['name'])

    with open('rules_per_app.csv', 'w') as csvfile:
        cw = csv.writer(csvfile)
        applications = list(map(list, applications.items()))
        for application in applications:
            cw.writerow([application[0]] + application[1])


if __name__ == '__main__':
    main()
