# OAuth2 Python

## Usage

### Setup
Create an OAuth2 application at the authorization entitiy and add `http://localhost:4074/` as a redirect URI 

### Code
Grant and authorize with

	auth = oauth2.OAuth2(clientId, clientSecret, authorizationURL, tokenURL)
	auth.authorize(scopes)

This (if not done already and the refresh token has been stored) will open the authorization url and let the user grant access. The code then gets the grant code thanks to a local HTTP server.

Get the access token for requests with

	auth.getAccessToken()

`getAccessToken()` makes sure the access token hasn't expired, and if it has it will be refreshed and the new token will be returend
