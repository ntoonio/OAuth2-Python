from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import time
import webbrowser
import requests
import base64
import json

class OAuth2:
	def __init__(self, clientId, clientSecret, authorizationURL, tokenURL):
		self._clientId = clientId
		self._clientSecret = clientSecret

		self._authorizationURL = authorizationURL
		self._tokenURL = tokenURL

		self._authorizationCode = ""

	def authorize(self, scopes, saveRefresh = True):
		if saveRefresh and self._readTokens():
			self._refreshAcessToken()
		else:
			self._openAuthorizationURL(scopes)
			tokens = self._getTokens()

			self.accessToken = tokens["access_token"]
			self.refreshToken = tokens["refresh_token"]
			self.expires = time.time() + tokens["expires_in"]

			if saveRefresh:
				self._writeToken()

	def getAccessToken(self, secondTry = False):
		if time.time() >= self.expires:
			if secondTry:
				raise Exception("Token still expired, something is wrong")
			print "Access token expired"
			self._refreshAcessToken()
			return self.getAccessToken(secondTry = True)

		return self.accessToken

	def _openAuthorizationURL(self, scopes):
		url = self._getAuthorizationURL(scopes)
		webbrowser.open(url)

		return self._getAuthorizationCode()

	def _getAuthorizationURL(self, scopes):
		return self._authorizationURL + "?" + "scope=" + " ".join(scopes) + "&response_type=code&client_id=" + self._clientId + "&redirect_uri=http://localhost:4074/"

	def _getAuthorizationCode(self):
		self.authorizationCode = ""

		server = HTTPServer(("", 4074), MakeGetAuthorizationCodeHandler(self))

		print "Waiting for authorization code"
		while self.authorizationCode == "":
			server.handle_request()

		return self.authorizationCode

	def _getTokens(self):
		data = {"grant_type": "authorization_code", "code": self.authorizationCode, "redirect_uri": "http://localhost:4074/"}

		r = requests.post(self._tokenURL, data=data, headers={"Authorization": "Basic " + base64.b64encode(self._clientId + ":" + self._clientSecret)})

		return json.loads(r.text)

	def _refreshAcessToken(self):
		data = {"grant_type": "refresh_token", "refresh_token": self.refreshToken}

		r = requests.post(self._tokenURL, data=data, headers={"Authorization": "Basic " + base64.b64encode(self._clientId + ":" + self._clientSecret)})

		tokens = json.loads(r.text)

		self.accessToken = tokens["access_token"]
		self.expires = time.time() + tokens["expires_in"]

		print "Refreshed acceses token"

	def _writeToken(self):
		file = open("token.json", "w")
		data = {"refresh_token": self.refreshToken}
		json.dump(data, file)
		file.close()

	def _readTokens(self):
		try:
			file = open("token.json", "r")
			data = json.load(file)

			self.refreshToken = data["refresh_token"]

			return True
		except IOError:
			return False

def MakeGetAuthorizationCodeHandler(OAuth2Class):
	class GetAuthorizationCodeHandler(BaseHTTPRequestHandler):
		def log_message(self, format, *args):
			return

		def do_GET(self):
			parsedPath = urlparse.urlparse(self.path)

			for q in parsedPath.query.split("&"):
				kv = q.split("=")

				if kv[0] == "code":
					OAuth2Class.authorizationCode = kv[1]

			self.send_response(200)
			self.end_headers()
			self.wfile.write("<script>window.close();</script>")

			return

	return GetAuthorizationCodeHandler