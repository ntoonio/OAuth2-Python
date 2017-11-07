import oauth2
import json

data = json.load(open("test_credentials.json", "r"))

# Create an application at https://developer.spotify.com/my-applications/#!/applications/create
# Add http://localhost:4074/ as redirect uri

clientId = data["clientId"]
clientSecret = data["clientSecret"]
authorizationURL = "https://accounts.spotify.com/authorize"
tokenURL = "https://accounts.spotify.com/api/token"

scopes = ["user-read-playback-state"]
saveRefreshToken = True

auth = oauth2.OAuth2(clientId, clientSecret, authorizationURL, tokenURL)
auth.authorize(scopes, saveRefreshToken)

print auth.getAccessToken()