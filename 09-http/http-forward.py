import urllib.request
import http.server
import urllib.error
import sys
import http.server
import urllib.request
import socket
import urllib.parse

schema = "http://"
# Get arguments
port = int(sys.argv[1])
upstream_url = sys.argv[2]


class RequestHandler(http.server.BaseHTTPRequestHandler):
	@staticmethod
	def form_request_url(up_url, path):
		host = urllib.parse.urlparse(up_url)[1]

		return schema + host + path

	@staticmethod
	def make_upstream_request(request_url, request_headers, request_content, request_timeout):
		req = urllib.request.Request(request_url)
		req.headers = request_headers

		r_code = r_headers = r_content = r_error = r_timeout = None

		try:
			# Check for content
			if request_content is not None:
				request_response = urllib.request.urlopen(req, data=request_content, timeout=request_timeout)
			else:
				request_response = urllib.request.urlopen(req, timeout=request_timeout)
		except urllib.error.HTTPError as e:
			r_error = e.code
			return r_code, r_headers, r_content, r_error, r_timeout
		except socket.timeout:
			r_error = False
			r_timeout = True
			return r_code, r_headers, r_content, r_error, r_timeout

		# Form request info, error and timeout are None
		r_code = request_response.getCode()
		r_headers = request_response.info()
		r_content = request_response.read()

		return r_code, r_headers, r_content, r_error, r_timeout

	def do_GET(self):
		request_path = self.path
		request_url = self.form_request_url(upstream_url, request_path)
		request_headers = self.headers
		request_content = None

		response = self.make_upstream_request(request_url, request_headers, request_content, request_timeout=1)

		if response[4] is not None:
			pass

		if response[3] is not None:
			pass

	def do_POST(self):
		pass


def run():
	server = http.server.HTTPServer(("", port), RequestHandler)

	server.serve_forever()
	print("listening on port " + str(port))


run()
