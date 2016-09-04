# JupyterHub Remote CSV Authenticator #

Simple authenticator for [JupyterHub](http://github.com/jupyter/jupyterhub/)
that fetches user authentication information from a CSV file over HTTP. Popular
use case is for maintaining authentication info in a Google Sheet.

## CSV Format ##

The authenticator expects the CSV to be in the following format:

| username  | password_hash        |
| ----------|----------------------|
| username1 | <hex-encoded-pbkdf2> |
| username2 | <hex-encoded-pbkdf2> |
| usernamen | <hex-encoded-pbkdf2> |

The headers must say `username` and `password_hash`. The username can be any
identifier, and the password_hash must be a hex representation of a [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2)
derived hash of the password, using the username as salt. The PBKDF2 iteration
count is configurable, and defaults to 1000.

One popular way to maintain this CSV file is with Google Sheets and the
JupyterHub RemoteCSV Google Sheets Helper. 

## Security Notes ##

If you need your JupyterHub installation to be highly secure, do *not* use this
Authenticator! It trades off some security for a lot of convenience, which might
or might not be the right tradeoff for your JupyterHub installation.

## Logging people out ##

If you make any changes to JupyterHub's authentication setup that changes
which group of users is allowed to login (such as changing the csv url,
removing access for individual users, or even just turning on a new Authenticator), you *have* to change the  jupyterhub cookie secret, or 
users who were previously logged in and did not log out would continue to be
logged in!

You can do this by deleting the `jupyterhub_cookie_secret` file. Note 
that this will log out *all* users who are currently logged in.

## Installation ##

```
pip install jupyterhub-remotecsv-authenticator
```

Should install it. It has no additional dependencies beyond JupyterHub.

You can then use this as your authenticator by adding the following line to
your `jupyterhub_config.py`:

```
c.JupyterHub.authenticator_class = remotecsvauthenticator.RemoteCSVAuthenticator'
```

## Configuration ##

RemoteCSVAuthenticator has one *required* configuration you must set, and 
several optional ones.

Don't forget the preceeding `c.` for setting configuration parameters! 
JupyterHub uses [traitlets](https://traitlets.readthedocs.io) for 
configuration, and the `c` represents the [config object](https://traitlets.readthedocs.io/en/stable/config.html).

### `RemoteCSVAuthenticator.csv_url` ###

HTTP / HTTPS URL to fetch the CSV from. Should return a CSV formatted 
according to the guidelines specified above. Must be utf-8 encoded.

This configuration is *required*.

```
c.RemoteCSVAuthenticator.csv_url = 'https://docs.google.com/spreadsheets/d/1JZhG3JQnm7st7mx2iEACtQt6Ita0fNTaatzBjz3plKo/pub?gid=0&single=true&output=csv'
```

### `RemoteCSVAuthenticator.cache_seconds` ###

Number of seconds to cache the response from `csv_url` before fetching again.
This is set to 5minutes (`300`) by default, to prevent us making a HTTP
request each time someone tries to log in. This is also the worst case
time you have to wait between adding a new user entry to your CSV and that
user being able to log in. Set this to `0` to disable the cache.

```
c.RemoteCSVAuthenticator.cache_seconds = 300
```
