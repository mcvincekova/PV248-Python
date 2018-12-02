import urllib.request
import http.server
import urllib.error
import sys
import http.server
import urllib.request
import socket
import urllib.parse
import json

schema = "http://"
# Get arguments
port = int(sys.argv[1])
upstream_url = sys.argv[2]
path_param = "/"


class RequestHandler(http.server.BaseHTTPRequestHandler):
	@staticmethod
	def get_headers_dict(headers):
		headers_dict = {}
		for header in headers.items():
			headers_dict[header[0]] = header[1]

		return headers_dict

	@staticmethod
	def check_valid_url(url_to_check):
		try:
			req = urllib.request.Request(url_to_check)
		except ValueError:
			return None

		return req

	@staticmethod
	def is_json_valid(request_body):
		return request_body is not None and "url" in request_body and \
		       (request_body["type"] == "POST" or "content" in request_body)

	@staticmethod
	def get_json(r_content):
		try:
			output_content = json.loads(r_content)
		except ValueError:
			return None

		return output_content

	@staticmethod
	def form_request_url(up_url, path):
		# https://docs.python.org/3/library/urllib.parse.html
		host = urllib.parse.urlparse(up_url)[1] if path_param in up_url else up_url

		return schema + host + path

	def make_upstream_request(self, request_url, request_headers, request_content, request_timeout):

		req = self.check_valid_url(request_url)
		if req is None:
			self.handle_error(None)
			return None
		req.headers = request_headers

		# handle: https://docs.python.org/3/library/urllib.error.html
		try:
			# Check for content
			if request_content is not None:
				request_response = urllib.request.urlopen(req, data=request_content, timeout=request_timeout)
			else:
				request_response = urllib.request.urlopen(req, timeout=request_timeout)
		except urllib.error.HTTPError as e:
			self.handle_error(e.code)
			return None
		except urllib.error.URLError as e:
			if isinstance(e.reason, socket.timeout):
				self.handle_timeout()
			else:
				self.handle_error(None)
			return None
		# hell yea timeouts, timeouts everywhere -> add socket timeout
		# http://devmartin.com/blog/2015/02/fun-with-urlerror-socket.timeout-and-pythons-urlopen.../
		except socket.timeout:
			self.handle_timeout()
			return None

		return request_response.getcode(), request_response.info(), request_response.read()

	def send_code_and_headers(self, code):
		self.send_response(code)
		self.end_headers()

	def handle_timeout(self):
		self.send_code_and_headers(200)
		output = {"code": "timeout"}
		self.wfile.write(bytes(json.dumps(output, indent=2, ensure_ascii=False), "utf-8"))

	def handle_error(self, r_code):
		self.send_code_and_headers(200)

		# Check whether the error response code
		output = {"code": "unknown error"} if r_code is None else {"code": r_code}
		self.wfile.write(bytes(json.dumps(output, indent=2, ensure_ascii=False), "utf-8"))

	def handle_response(self, response):
		# Error / timeout encountered and handled, end
		if response is None:
			return

		# Extract response parts: r_code, r_headers, r_content
		r_code = response[0]
		r_headers = response[1]
		r_content = response[2]

		headers = self.get_headers_dict(r_headers)
		output = {"headers": headers,
		          "code": r_code}

		response_content = self.get_json(r_content)
		if response_content is not None:
			output["json"] = response_content
		else:
			# Do not include the invalid json
			output["content"] = r_content.decode("utf-8")

		self.send_response(200)
		content_length = len(bytes(json.dumps(output, indent=2, ensure_ascii=False), "utf-8"))
		# Check for content
		if content_length is not None:
			self.send_header("Content-Length", content_length)
		self.end_headers()
		self.wfile.write(bytes(json.dumps(output, indent=2, ensure_ascii=False), "utf-8"))

	def do_GET(self):
		request_path = self.path
		# Get request url
		request_url = self.form_request_url(upstream_url, request_path)

		request_headers = self.headers
		request_content = None
		# Perform upstream request
		response = self.make_upstream_request(request_url, request_headers, request_content, request_timeout=1)
		self.handle_response(response)

	def do_POST(self):
		# Read body
		headers = self.headers
		content_length = headers["Content-length"]

		if content_length:
			c_length = int(content_length)
		else:
			c_length = 0

		r_data = self.rfile.read(c_length).decode("utf-8")
		request_body = self.get_json(r_data)

		# Check for invalid json, if so handle and end
		if not self.is_json_valid(request_body):
			self.send_code_and_headers(200)
			output = {"code": "invalid json"}
			self.wfile.write(bytes(json.dumps(output, indent=2, ensure_ascii=False), "utf-8"))
			return

		# Form request info
		if request_body is not None and (request_body["type"] == "GET" or "type" not in request_body):
			request_body["type"] = "GET"
		else:
			request_body["type"] = "POST"

		request_url = request_body["url"]
		request_headers = request_body["headers"] if "headers" in request_body else {}
		# Default timeout is 1s
		request_timeout = request_body["timeout"] if "timeout" in request_body else 1

		if request_body["type"] == "GET":
			request_content = None
		else:
			request_content = bytes(request_body["content"], "utf-8")

		response = self.make_upstream_request(request_url, request_headers, request_content, request_timeout)
		self.handle_response(response)


def run():
	server = http.server.HTTPServer(("", port), RequestHandler)

	server.serve_forever()
	# print("listening on port " + str(port))
	server.server_close()


run()
