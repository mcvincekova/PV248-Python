import http.client
import http.server
import socketserver
import sys


class RequestHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		pass

	def do_POST(self):
		pass


def run():
	port = int(sys.argv[1])
	hostname = sys.argv[2]

	# https://wiki.python.org/moin/BaseHttpServer
	httpd = socketserver.TCPServer(("", port), RequestHandler)

	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass

	httpd.server_close()


run()
