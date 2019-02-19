# auth0-reporting-tools

This repo contains python scripts for working with the Auth0 Management API.

## Authorization Code Grant Flow with PKCE

The scripts in this project authenticate using the [Authorization Code Grant
Flow with PKCE](https://auth0.com/docs/api-auth/tutorials/authorization-code-grant-pkce).
The process opens a browser window to handle the authentication, and starts a
local webserver to receive the callback and the authorization code. The code is
then exchanged for an access token. The access token is then used to access the
Management API.

In addition we use the [state parameter](https://auth0.com/docs/protocols/oauth2/oauth-state)
(as a nonce) to ensure against replay attack.

## Getting Started

### Configuring the Local Environment

Pick a location for the virtualenv, initialize and activate it. For example:

```shell
mkdir -p ~/virtualenv/auth0-reporting-tools
virtualenv ~/virtualenv/auth0-reporting-tools
source ~/virtualenv/auth0-reporting-tools/bin/activate
```

Choose a location for the repository, clone it, and install the required
modules. For example:

```shell
mkdir ~/git
cd ~/git
git clone git@github.com:dmark/auth0-reporting-tools.git
cd auth0-reporting-tools
pip install -r requirements.txt
```

### Configuring Auth0

1. Create a [Native app](https://auth0.com/docs/applications/guides/register-native-app) for the command line tool to communicate with.
1. Add "http://127.0.0.1:3000/callback" to the list of allowed callback URLs.
1. Add an [application metadata configuration variable](https://auth0.com/docs/dashboard/reference/settings-application#application-metadata) setting "ManagementAPIAccess" to "True".
1. Using the file `dot_env.example` as a template, create a `.env` file with your tenant and application settings. For example:

```
AUTH0_DOMAIN=mytennant.auth0.com
AUTH0_CLIENT_ID=abc123
AUTH0_CLIENT_SECRET=def456
AUTH0_CALLBACK_URL=http://127.0.0.1:3000/callback
AUTH0_AUDIENCE=https://mytennant.auth0.com/api/v2/
```

1. Create a new rule using the file `rules_per_app.js` as a template. Replace "YOUR_TENANT" and update the scopes as needed.
1. Authorize users by adding "ManagementAPIAccess" to their `app_metadata` as follows:

```json
"app_metadata": {
  "rules": [
    "ManagementAPIAccess"
  ]
}
```

## Running the Script

With teh virtuend activated as above, run the script:

```shell
python rules_per_app.py
```

A browser window or tab will open with the Universal Login login page loaded.
After authenticating you can close the tab or window and return to your
terminal. For technical reasons, it is difficult to kill the browser window
automatically.

At this point the script will process your applications and rules, printing a
CSV file to stdout.
