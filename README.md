# auth0-reporting-tools

[![CircleCI](https://circleci.com/gh/dmark/auth0-reporting-tools/tree/master.svg?style=svg)](https://circleci.com/gh/dmark/auth0-reporting-tools/tree/master)

This repository contains python scripts for working with the Auth0 Management
API.

References:

* An Overview of Auth0: https://auth0.com/docs/getting-started/overview
* Getting Started with Auth0: https://auth0.com/docs/getting-started/the-basics

## Configuring Auth0

### The Application

Please note, the language here can get a bit confusing because of a double use
of the word “application”, meaning both your actual application (your website
or API) and the "Application" entity you create the Management Console.

We begin by creating an [Application](https://auth0.com/docs/applications)
within the [Auth0 Management Console](https://manage.auth0.com/). Creating an
Application is how you register your actual application (in this case the
command line tools in this software repository) with Auth0. You would typically
create a new Application in the Management Console for each of your actual
applications.

After logging in to the Auth0 Management Console, click the “Applications” link
in the top left corner of the screen, then click the "[Create
Application](https://auth0.com/docs/applications/guides/register-native-app)"
button in the top right corner of the screen.

![Applications](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.13.23.png)

When you click the “Create Application” button in the Management Console,
you’ll get a pop-up window within which you will give the application a name
(of your choosing, can be anything, but should describe what the application is
for) and you will select what “type” of application this will be. There are
four "type" options, one of which is “Native App”. For our purposes, this is
the option you will choose.

![Create Application](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.11.09.png)

One of the key differences between the application types is the [authentication
method](https://auth0.com/docs/applications/reference/grant-types-available)
(often referred to as “grant type” or “flow”) used between your actual
application and Auth0. In the documentation below you will see mention of
“[Authorization Code Grant Flow with
PKCE](https://auth0.com/docs/flows/concepts/mobile-login-flow)”. This is the
authentication flow required by the command line tools in this repository, and
is the authentication flow used by the Native App application type.

Once you click Create, you will land on the “[Quick
Start](https://auth0.com/docs/quickstarts)” tab for the application you just
created. You can have a look at the Quickstarts (ready made code examples for
testing) if you like, but this is not necessary for our purposes.

![Quick Start](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.11.30.png)

Skip over to the
[Settings](https://auth0.com/docs/dashboard/reference/settings-application)
tab. Notice at the top of the Settings page the “Domain” and “Client ID”
values. _You should record these values someplace convenient_, as you will need
them later in the setup process.

![Settings](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.24.46.png)

On the Settings page, scroll about half way down to the "Allowed Callback URLs"
text box. Add "http://127.0.0.1:3000/callback" (without the quotes) in the text
box.

![Callbacks](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.07.png)

Further down the page, I would suggest setting the “JWT Expiration” to 300
seconds. It is [generally a good idea to keep this expiration time
short](https://auth0.com/docs/best-practices/application-settings).

Scroll all the way to the bottom, and click “[Show Advanced
Settings](https://auth0.com/docs/dashboard/reference/settings-application#advanced-settings)”.
You will see the “Application Metadata” screen. Add “ManagementAPIAccess”
(without the quotes) in the “Key” field, “True” in the “Value” field, and then
click Create.  This feature will be used as part of our access control
mechanism.

![Metadata](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.24.png)

And finally, click Save Changes.

While we’re here, scroll all the way back to the top and click the Connections
tab on the right (not the Connections link in the left side menu). Confirm your
user database is enabled (green means yes) or, if it is not enabled, click the
toggle beside your user database name to enable it.

![Connections](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.49.png)

### The Rule

[Rules](https://auth0.com/docs/rules) are snippets of JavaScript code that run
when a user logs in. Rules allow you to customize the Auth0 service in many
useful ways. Refer to [this](https://github.com/auth0/rules) repository for
examples. For our purposes we will create a rule that controls access to our
Auth0 Application (and therefore, controls who is allowed to use the command
line tools in this repository).

In the Auth0 Management Console, click the Rules link in the left side menu,
then click [Create Rule](https://auth0.com/docs/rules/guides/create).

![Rules](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.45.20.png)

From the "Pick a Rule Template" page, select the "Empty Rule".

![Rule Template](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.49.58.png)

The Edit Rule page will open. Give the rule a meaningful name, something
descriptive like "Access control for reporting tools". Delete the code in the
code box, then copy the code from the file `rules_per_app.js` in this software
repository, and paste it into the now empty code box. Replace the text
'[YOUR_TENANT]' with the name of your own tenant, then click Save.

![Edit Rule](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.54.30.png)

### The Users

Previously we added some "metadata" to the Application we created above, and we
said that it will be part of our access control mechanism, which also includes
the rule you just created. The last piece of the access control mechanism will
be authorizing users to use the command line tools.

You will authorize users by adding a similar piece of metadata to their
profiles in Auth0. Start by clicking the Users link in the left side menu in
the Auth0 Management Console. From here you can create a new user, or search
for an existing user. For this example I will use an existing user.

![Users](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.03.37.png)

Click on the user's name field to open their profile page.

![User](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.04.46.png)

Scroll down to "Metadata" and edit the users `app_metadata` text box to include
`ManagementAPIAccess` under `roles` as follows:

```json
"app_metadata": {
  "roles": [
    "ManagementAPIAccess"
  ]
}
```

If there is an existing "roles" list, you will need to add the new role to the list like so:

```json
"app_metadata": {
  "roles": [
    "ARole",
    "AnotherRole",
    "ManagementAPIAccess"
  ]
}
```

The end result will look something like what is below. You can ignore, and do
not change, and other data in the metadata text boxes.

![App Metadata](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.04.57.png)

Click Save. Repeat this process for all users who are authorized to use the
reporting tools in this software repository.

## Configuring the Local Environment

Assumptions for the following steps:

1. You are running on a reasonably up to date Mac or Linux computer,
1. You have access to a terminal window and understand how to use it,
1. You have the following tools installed:
  1. [Python 3](https://www.python.org/downloads/)
  1. Virtualenv
  1. [Git](https://git-scm.com/downloads)

From a terminal window you will create a “[virtualenv
environment](https://virtualenv.pypa.io/en/latest/)”, which will function as a
repository for the supporting software required to run the reporting tools in
this repository. You will create a directory (or “folder”) of your choosing,
run the virtualenv command against that directory, and then “activate” the
virtualenv as follows.

In the example below I have created a directory called “demo” in my home directory, and directories below that to hold the virtualenv and the actual software.

```
demo$ mkdir -p ~/demo/venv/python-reporting-tools
demo$ virtualenv ~/demo/venv/python-reporting-tools
demo$ source ~/demo/venv/python-reporting-tools/bin/activate
(python-reporting-tools) demo$
```

You will likely now see the name of the virtualenv (python-reporting-tools) displayed as part of the command line. This lets you know the virtualenv is active.

Next you will download the `rules_per_app.py` software repository into a location of your choosing, and install any supporting software. The supporting software will be installed into your virtualenv environment which means, whenever you want to run these tools, you need to activate the virtualenv first, using the `source` command demonstrated above.

```
(python-reporting-tools) demo$ mkdir ~/demo/git
(python-reporting-tools) demo$ cd ~/demo/git
(python-reporting-tools) demo$ git clone git@github.com:dmark/auth0-reporting-tools.git
(python-reporting-tools) demo$ cd auth0-reporting-tools
(python-reporting-tools) demo$ pip install -r requirements.txt
```

The “git clone” command copies the software from where it is stored online to your local machine. The “pip install” command will install the supporting software into the virtualenv environment.

You are almost ready to run the reporting tool. The last step is to let the tool know about your own Auth0 environment by creating a `.env` environment file with the details of your Auth0 tenant. Using the file `dot_env.example` as a template, you will create a new file called `.env` (note the ‘.’ in front of the name … that’s important!), which will look like the following:

```
AUTH0_CLIENT_ID=${CLIENT_ID}
AUTH0_CLIENT_SECRET=${CLIENT_SECRET}
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_DOMAIN=${TENANT_NAME}.auth0.com
AUTH0_AUDIENCE=https://${AUTH0_DOMAIN}/api/v2/
AUTH0_RESPONSE_TYPE=code
AUTH0_GRANT_TYPE=authorization_code
AUTH0_SCOPES=profile openid email read:clients read:rules
AUTH0_CODE_CHALLENGE_METHOD=S256
```

You will need to replace the fields surrounded by `${ }` with values from your Auth0 environment. You recorded the necessayr values when you created the Application above. When you are done, the file will look similar to the following, but with your own Auth0 tenant and application data:

```
AUTH0_CLIENT_ID=wppCywAmtNf7o0eTACcGl40X6ta0I5y1
AUTH0_CLIENT_SECRET=
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_DOMAIN=markdrummond.auth0.com
AUTH0_AUDIENCE=https://markdrummond.auth0.com/api/v2/
AUTH0_RESPONSE_TYPE=code
AUTH0_GRANT_TYPE=authorization_code
AUTH0_SCOPES=profile openid email read:clients read:rules
AUTH0_CODE_CHALLENGE_METHOD=S256
```

The `CLIENT_ID` and `TENANT_NAME` values you can get from the Settings page of the Auth0 Application you created previously. The `CLIENT_SECRET` can be left blank, and the remaining fields can be left alone.

If all is well, you can now test the login process by running the following command from the terminal:

```shell
(python-reporting-tools) demo$ python login.py
```

A browser tab or window will open asking you to log in. You will log in as one of the users you have authorized to use the tool. After logging in, you can close the window or tab, go back to the terminal window, and you should see some rather technical looking output on the screen. It will look something like the following. This means the login was successful:

```shell
(python-reporting-tools) demo$ python login.py 
{'iss': 'https://markdrummond.auth0.com/', 'sub': 'auth0|5c6b52fd451bd02197ecbd5f', 'aud': 'https://markdrummond.auth0.com/api/v2/', 'iat': 1550778507, 'exp': 1550864907, 'azp': 'wppCywAmtNf7o0eTACcGl40X6ta0I5y1', 'scope': 'read:rules read:clients'}
```

If that worked, then you can run the reporting tool as follows:

```
(python-reporting-tools) demo$ python rules_per_app.py
```

Another browser tab will open, but you will likely be logged in automatically since you just logged in above, and after a short period of time you should find a CSV file called “rules_per_app.csv” in the directory where you are currently located. You can open the file in a spreadsheet application like Excel, format and modify it as needed.

## Authorization Code Grant Flow with PKCE

The scripts in this project authenticate using the [Authorization Code Grant
Flow with PKCE](https://auth0.com/docs/api-auth/tutorials/authorization-code-grant-pkce).
The process opens a browser window to handle the authentication, and starts a
local webserver to receive the callback and the authorization code. The code is
then exchanged for an access token. The access token is then used to access the
Management API.

In addition we use the [state parameter](https://auth0.com/docs/protocols/oauth2/oauth-state)
(as a nonce) to protect against replay attacks.

The Authorization Code Grant Flow with PKCE code used here is based on
[this](https://github.com/gateley-auth0/CLI-PKCE) project previously created by
[Auth0 Professional Services](https://auth0.com/professional-services/).
