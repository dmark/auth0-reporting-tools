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

Scroll all the way to the bottom, and click “Show Advanced Settings”. You will see the “Application Metadata” screen. Add “ManagementAPIAccess” (without the quotes) in the “Key” field, “True” in the “Value” field, and then click Create.

![Metadata](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.24.png)

And finally, click Save Changes.

While we’re here, scroll all the way back to the top and click the Connections tab on the right (not the Connections link in the left side menu). Confirm your user database is enabled (green means yes) or, if it is not enabled, click the toggle beside your user database name to enable it.

![Connections](https://github.com/dmark/auth0-reporting-tools/blob/updates-documentation/images/Screenshot%202019-02-20%2019.18.49.png)

#### The Rule

Rules are snippets of JavaScript that execute when a user logs in, allowing you
to customize the service in [many ways](https://github.com/auth0/rules).

You will create a [rule](https://auth0.com/docs/rules) that controls who has
access to the command line utility. Follow the steps outlined
[here](https://auth0.com/docs/rules/guides/create) to create a new rule, using
the code from the file `rules_per_app.js` as a template. The only change you
need to make to the rule is to replace "YOUR_TENANT" with the actual name of
your Auth0 tenant. You can optionally update the scopes as needed.

#### The Users

You will authorize users by adding `ManagementAPIAccess` to their
`app_metadata` as follows:

```json
"app_metadata": {
  "rules": [
    "ManagementAPIAccess"
  ]
}
```

### Configuring the Local Environment

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
