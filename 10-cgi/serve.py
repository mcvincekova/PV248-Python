import sys

port = int(sys.argv[1])
directory_path = sys.argv[2]


class CgiRequestHandler:
	def __init__(self, port, directory_path):
		self.port = port
		self.directory_path = directory_path

	def set_request_meta_variables(self):
		pass

		# AUTH_TYPE
		# CONTENT_LENGTH
		# CONTENT_TYPE
		# GATEWAY_INTERFACE
		# PATH_INFO
		# PATH_TRANSLATED
		# QUERY_STRING
		# REMOTE_ADDR
		# REMOTE_HOST
		# REMOTE_IDENT
		# REMOTE_USER
		# REQUEST_METHOD
		# SCRIPT_NAME
		# SERVER_NAME
		# SERVER_PORT
		# SERVER_PROTOCOL
		# SERVER_SOFTWARE


def run():
	cgi_request_handler = CgiRequestHandler(port, directory_path)
