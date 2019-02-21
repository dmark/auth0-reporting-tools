#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""apps_and_rules.py -- Writes to a file a CSV file mapping rules to
applications. Each line of the CSV represents a single application and all the
rules that apply to that application.
"""
import csv
import re
import requests

import auth_env
import auth_token
import login


def get_data(env, token, data):
    headers = {'Authorization': 'Bearer %s' % token['access_token']}
    url = env['audience'] + data
    return requests.get(url, headers=headers).json()


def main():
    """main"""

    env = auth_env.load_env()
    code = login.authenticate(env)
    token = auth_token.get_access_token(code, env)

    # try:
    #     validate_token(token, jwks, env)
    # except:
    #     return 'error: token validation error'

    rules = get_data(env, token, 'rules')
    clients = get_data(env, token, 'clients')

    # Create a dictionary of lists, with client names as the keys
    applications = {}
    for client in clients:
        # Skip the "All Applications" pseudo-app
        if client['name'] == "All Applications":
            continue
        applications[client['name']] = []

    for rule in rules:
        # Skip rules that are disabled
        #if rule['enabled'] is False:
        #    continue

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

    # Convert applications{} to a CSV and save it to a file
    with open('rules_per_app.csv', 'w') as csvfile:
        cw = csv.writer(csvfile)
        applications = list(map(list, applications.items()))
        for application in applications:
            cw.writerow([application[0]] + application[1])


if __name__ == '__main__':
    main()
