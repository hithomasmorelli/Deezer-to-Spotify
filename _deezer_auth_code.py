##
## THIS CODE IS EXTRACTED AND MODIFIED FROM 
## https://github.com/helpsterTee/spotify-playlists-2-deezer/blob/b6e3621b4b778ab11a8ce59d0973c603fda99e2d/spotify-restore.py#L143-L200
##
## ACCORDINGLY, THE REPOSITORY LICENSE DOES NOT APPLY TO THIS FILE,
## AND THE FOLLOWING LICENSE (FROM https://github.com/helpsterTee/spotify-playlists-2-deezer/blob/85a405dbf6df161cf63a89494a7009915e5ade25/LICENSE)
## APPLIES TO THIS FILE, AND THIS FILE ONLY
##

'''
MIT License

Copyright (c) 2017 Thomas
Copyright (c) 2020 Thomas Morelli <me@thomasmorelli.me>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import re
import http.client
import http.server
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

## Authorize code
def authorize(app_id, secret, scope):
	webbrowser.open('https://connect.deezer.com/oauth/auth.php?' + urllib.parse.urlencode({
		'app_id': app_id,
		'redirect_uri': 'http://localhost:8080/authfinish',
		'perms': scope
	}))

	# Start a simple, local HTTP server to listen for the authorization token... (i.e. a hack).
	server = _AuthorizationServer('localhost', 8080)
	try:
		while True:
			server.handle_request()
	except _Authorization as auth:
		return get_actual_token(app_id, secret, auth.access_token)

class _AuthorizationServer(http.server.HTTPServer):
	def __init__(self, host, port):
		http.server.HTTPServer.__init__(self, (host, port), _AuthorizationHandler)

	# Disable the default error handling.
	def handle_error(self, request, client_address):
		raise

class _AuthorizationHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		# Read access_token and use an exception to kill the server listening...
		if self.path.startswith('/authfinish?'):
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write(b'<script>close()</script>Thanks! You may now close this window.')
			raise _Authorization(re.search('code=([^&]*)', self.path).group(1))

		else:
			self.send_error(404)

	# Disable the default logging.
	def log_message(self, format, *args):
		pass

class _Authorization(Exception):
	def __init__(self, access_token):
		self.access_token = access_token

# the other one is actually a "code", so now get the real token
def get_actual_token(app_id, secret, code):
	f = urllib.request.urlopen("https://connect.deezer.com/oauth/access_token.php?app_id="+app_id+"&secret="+secret+"&code="+code)
	fstr = f.read().decode('utf-8')

	if len(fstr.split('&')) != 2:
		raise Exception

	stri = fstr.split('&')[0].split('=')[1]
	token = stri
	return token