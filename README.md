# auth0-reporting-tools

[![CircleCI](https://circleci.com/gh/dmark/auth0-reporting-tools/tree/master.svg?style=svg)](https://circleci.com/gh/dmark/auth0-reporting-tools/tree/master)

This repository contains python scripts for working with the Auth0 Management API.

## Getting Started

### Configuring Auth0

#### The Application

Please note, the language here can get a bit confusing because of a double use of the word “application”, meaning both your actual application (your website or API) and the "Application" entity you create the Management Console.

We begin by creating an [Application](https://auth0.com/docs/applications) within the [Auth0 Management Console](https://manage.auth0.com/). Creating an Application is how you register your actual application (in this case the command line tools in this software repository) with Auth0. You would typically create a new Application in the Management Console for each of your actual applications.

After logging in to the Auth0 Management Console, click the “Applications” link in the top left corner of the screen, then click the "Create Application" button in the top right corner of the screen.

![Applications](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.13.23.png)

When you click the “Create Application” button in the Management Console, You’ll get a pop-up window within which you will give the application a name (of your choosing, can be anything, but should describe what the application is for) and you will select what “type” of application this will be. There are four "type" options, one of which is “Native App”. For our purposes, this is the option you will choose.

![Create Application](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.11.09.png)

One of the key differences between the application types is the authentication method (often referred to as “grant type” or “flow”) used between your actual application and Auth0. In the documentation below you will see mention of “Authorization Code Grant Flow with PKCE”. This is the authentication flow required by the command line tools in this repository, and is the authentication flow used by the Native App application type.

Once you click Create, you will land on the “Quick Start” tab for the application you just created. You can have a look at the Quickstarts (ready made code examples for testing) if you like, but this is not necessary for our purposes.

![Quick Start](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.11.30.png)

Skip over to the Settings tab. Notice at the top of the Settings page the “Domain” and “Client ID” values. You should record these values someplace convenient, as you will need them later in the setup process.

![Settings](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.24.46.png)

On the Settings page, scroll about half way down to the "Allowed Callback URLs" text box. Add "http://127.0.0.1:3000/callback" (without the quotes) in the text box.

![Callbacks](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.07.png)

Further down the page, I would suggest setting the “JWT Expiration” to 300 seconds. It is generally a good idea to keep this expiration time short.

Scroll all the way to the bottom, and click “Show Advanced Settings”. You will see the “Application Metadata” screen. Add “ManagementAPIAccess” (without the quotes) in the “Key” field, “True” in the “Value” field, and then click Create. This feature will be used as part of our access control mechanism.

![Metadata](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.24.png)

And finally, click Save Changes.

While we’re here, scroll all the way back to the top and click the Connections tab on the right (not the Connections link in the left side menu). Confirm your user database is enabled (green means yes) or, if it is not enabled, click the toggle beside your user database name to enable it.

![Connections](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.49.png)

#### The Rule

Rules are snippets of JavaScript code that run when a user logs in. Rules allow you to customize the Auth0 service in many useful ways. Refer to [this](https://github.com/auth0/rules) repository for examples. For our purposes we will create a rule that controls access to our Auth0 Application (and therefore, controls who is allowed to use the command line tools in this repository).

In the Auth0 Management Console, click the Rules link in the left side menu, then click Create Rule.

![Rules](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.45.20.png)

From the "Pick a Rule Template" page, select the "Empty Rule".

![Rule Template](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.49.58.png)

The Edit Rule page will open. Give the rule a meaningful name, something scriptive like "Access control for reporting tools". Delete the code in the code box, then copy the code from the file `rules_per_app.js` in this software repository, and paste it into the now empty code box. Replace the text '[YOUR_TENANT]' with the name of your own tenant, then click Save.

![Edit Rule](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2020.54.30.png)

#### The Users

Previously we added some "metadata" to the Application we created above, and we said that it will be part of our access control mechanism, which also includes the rule you just created. The last piece of the access control mechanism will be authorizing users to use the command line tools.

You will authorize users by adding a similar piece of metadata to their profiles in Auth0. Start by clicking the Users link in the left side menu in the Auth0 Management Console. From here you can create a new user, or search for an existing user. For this example I will use an existing user.

![Users](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.03.37.png)

Click on the user's name field to open their profile page.

![User](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.04.46.png)

Scroll down to "Metadata" and edit the users `app_metadata` text box to include `ManagementAPIAccess` under `roles` as follows:

```json
"app_metadata": {
  "roles": [
    "ManagementAPIAccess"
  ]
}
```

![App Metadata](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-21%2021.04.57.png)

### Configuring the Local Environment


You can ignore the quick starts. They are just sample applications that Auth0 provides, that allow a new Auth0 user to quickly “kick the tires” of the Auth0 service. For our purposes they are completely optional. If you have any developers on staff, they may be interested in the quickstarts as a means to getting up to speed. On that note, I’ve included details next steps below, but if you have any developers available, I would suggest getting them involved. This can be a complex process!

Assuming everything in Auth0 is set up, you will need now need to download the software and configure it to run. There are a lot of variables in these next steps so I’ll need to make some assumptions to keep this reasonably concise. My assumptions:

You are running on a reasonably up to date Mac or Linux computer,
You have access to a terminal window and understand how to use it,
You have the following tools installed:
Python 3 (I am using 3.7.2)
Virtualenv
Git

From a terminal window you will create a “virtualenv environment”, which will function as a repository for the supporting software required to run the rules_per_app.py tool. You will create a directory (or “folder” if you prefer) of your choosing, run the virtualenv command against that directory, and then “activate” the virtualenv as follows.

In the example below I have created a directory called “demo” in my home directory, and directories below that to hold the virtualenv and the actual software.

$ mkdir -p ~/demo/venv/python-reporting-tools
$ virtualenv ~/demo/venv/python-reporting-tools
$ source ~/demo/venv/python-reporting-tools/bin/activate

You will likely now see the name of the virtualenv (python-reporting-tools) displayed on your screen. This lets you know the virtualenv is active.

Next you will download the rules_per_app.py software into a location of your choosing, and install any supporting software. The supporting software will be installed to your virtualenv which means, whenever you want to run the scripts I have provided, you need to activate the virtualenv first, using the “source” command demonstrated above.

$ mkdir ~/demo/git
$ cd ~/demo/git
$ git clone git@github.com:dmark/auth0-reporting-tools.git
$ cd auth0-reporting-tools
$ pip install -r requirements.txt

“git clone” copies the software from where it is stored online to your local machine. The “pip install” command will install the supporting software into the virtualenv environment.

You are almost ready to run the reporting tool. The last step is to let the tool know about your own Auth0 environment by creating a “.env” environment file with the details of your Auth0 tenant. Using the file “dot_env.example” as a template, you will create a new file called “.env” (note the ‘.’ in front of the name … that’s important!), which will look like the following:

AUTH0_CLIENT_ID=${CLIENT_ID}
AUTH0_CLIENT_SECRET=${CLIENT_SECRET}
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_DOMAIN=${TENANT_NAME}.auth0.com
AUTH0_AUDIENCE=https://${AUTH0_DOMAIN}/api/v2/
AUTH0_RESPONSE_TYPE=code
AUTH0_GRANT_TYPE=authorization_code
AUTH0_SCOPES=profile openid email read:clients read:rules
AUTH0_CODE_CHALLENGE_METHOD=S256

You will need to replace the fields surrounded by “${ }” with values from your Auth0 environment. When you are done, the file will look similar to the following (with your Auth0 data rather than mine!):

AUTH0_CLIENT_ID=wppCywAmtNf7o0eTACcGl40X6ta0I5y1
AUTH0_CLIENT_SECRET=
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_DOMAIN=markdrummond.auth0.com
AUTH0_AUDIENCE=https://markdrummond.auth0.com/api/v2/
AUTH0_RESPONSE_TYPE=code
AUTH0_GRANT_TYPE=authorization_code
AUTH0_SCOPES=profile openid email read:clients read:rules
AUTH0_CODE_CHALLENGE_METHOD=S256

The client ID and domain values you can get from the Settings page of the Auth0 Application you created previously (the fourth screenshot in the list of screenshots I sent). The client secret can be left blank, and the remaining fields can be left alone.

If all is well, you can now test the login process by running the following command from the terminal:

$ python login.py

A browser tab or window will open asking you to log in. You will log in as one of the users you have authorized to use the tool. After logging in, you can go back to the terminal and you should see some rather technical looking output on the screen. It will look something like the following. This means the login was successful:

$ python login.py 
{'iss': 'https://markdrummond.auth0.com/', 'sub': 'auth0|5c6b52fd451bd02197ecbd5f', 'aud': 'https://markdrummond.auth0.com/api/v2/', 'iat': 1550778507, 'exp': 1550864907, 'azp': 'wppCywAmtNf7o0eTACcGl40X6ta0I5y1', 'scope': 'read:rules read:clients'}
$

If that worked, then you can run the reporting tool as follows:

$ python rules_per_app.py

Another browser tab will open, but you will likely be logged in automatically since you just logged in above, and after a short period of time you should find a CSV file called “rules_per_app.csv” in the directory where you are currently located. You can open the file in a spreadsheet application like Excel, format and modify it as needed.

I have included at the link below a copy of all the input and output from a terminal window from the above process. There’s a lot there, but you can see the results of each step. I definitely suggest engaging a developer to assist!

https://pastebin.com/wPXNmV0v

Let me know how you make out.

#### Setting up the `virtualenv`

We will use a [`virtualenv`](https://virtualenv.pypa.io/en/stable/) to configure
the project, so make sure you have `virtualenv` installed. Pick a location for
the virtualenv, initialize and activate it. For example:

```shell
mkdir -p ~/virtualenv/auth0-reporting-tools
virtualenv ~/virtualenv/auth0-reporting-tools
source ~/virtualenv/auth0-reporting-tools/bin/activate
```

#### Setting up the Software

With the vitualenv activated as above, choose a location for to clone the
code repository, clone it, and install the required modules. For example:

```shell
mkdir ~/git
cd ~/git
git clone git@github.com:dmark/auth0-reporting-tools.git
cd auth0-reporting-tools
pip install -r requirements.txt
```

Using the file `dot_env.example` as a template, create a `.env` file in the
root directory of the cloned repository from above, using your own tenant and
application settings. You can get the values for AUTH0_DOMAIN, AUTH0_CLIENT_ID,
and AUTH0_AUDIENCE from the Management Console of your Auth0 tenant. The first
two can be found on the setting page of the application you configured above.
The last can be found under the "APIs" menu, listed next to the name of the
Management API, labelled "API Audience".

Note that the AUTH0_CLIENT_SECRET is not required when using the Authorization
Code Grant Flow with PKCE.

```shell
AUTH0_DOMAIN=mytennant.auth0.com
AUTH0_CLIENT_ID=abc123
AUTH0_CLIENT_SECRET=
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_AUDIENCE=https://mytennant.auth0.com/api/v2/
```

## Running the Script

With the virtualenv activated as above, run the script:

```shell
python rules_per_app.py
```

A browser window or tab will open with the Universal Login login page loaded.
After authenticating you can close the tab or window and return to your
terminal. For technical reasons, it is difficult to close the browser window
automatically.

At this point the script will process your applications and rules, printing a
CSV file to the file 'rules_per_app.csv'. Each line of the CSV begins with an
application name, followed by the rules applicable to that application. The
rules are sorted so they are always in the same order, and if a rule does not
apply to a given application, that "cell" in the CSV is empty.

It is important to note that the script looks specifically for the use of the
`context.clientName` parameter in the rules.

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
