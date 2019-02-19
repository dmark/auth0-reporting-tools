# auth0-reporting-tools

This repo contains python scripts for working with the Auth0 Management API.

## Getting Started

Pick a location for the virtualenv, initialize and activate it. For
example:

```shell
mkdir -p ~/virtualenv/auth0-reporting-tools
virtualenv ~/virtualenv/auth0-reporting-tools
source ~/virtualenv/auth0-reporting-tools/bin/activate
```

Choose a location for the repository and clone it. For example:

```shell
mkdir ~/git
cd ~/git
git clone git@github.com:dmark/auth0-reporting-tools.git
cd auth0-reporting-tools
pip install -r requirements.txt
```

The scripts depend on a [machine-to-machine (M2M)
application](https://auth0.com/docs/api/management/v2/create-m2m-app)
with the client credentials stored in a `.env` file in the project directory.
The client must be authorized to access the Management API, and must have the
appropriate scopes assigned.  Copy `dot_env.example` to `.env`, edit, run
`python auth0 -t`. That should dump a list of all the connections for whichever
tenant you have configured in `.env`.

## Authorization Code with PKCE

The scripts in this project authenticate using the [Authorization Code
Grant Flow with PKCE](https://auth0.com/docs/api-auth/tutorials/authorization-code-grant-pkce).
The process opens a browser window to handle the authentication. The
resulting token is used to access the management API.

In addition we use the [state parameter](https://auth0.com/docs/protocols/oauth2/oauth-state)
(as a nonce) to ensure against replay attack.

## Running the App

To run the sample, make sure you have `python` and `pip` installed.

* You will need to create your app as a [Native app](https://auth0.com/docs/applications/guides/register-native-app).
* Populate .env with the client ID and tenant for your Auth0 app.
* Run `pip install -r requirements.txt` to install the dependencies.
* Run `python login.py`.

The python script will open up a window in your browser to log in.
* Log in

The browser window will tell you to return to your app (for technical
reasons, it is difficult to kill the browser window automatically)

* Return to your shell

The app will list the clients available in the tenant (by accessing
the management API).

# Security considerations

Access controlled with a rule. Refer to rules_per_app.js.

Th app metadata should have `ManagementAPIAccess = True` in application
metadata, and a user should have their app metada include
`ManagementAPIAccess` in their roles

META: INSERT Auth0 FOOTER HERE