import sys
import pathlib
import asyncio
from subprocess import TimeoutExpired

from aiohttp import web
import os
import mailbox


class CgiRequestHandler:
	def __init__(self, port, directory_path):
		self.port = port
		self.directory_path = directory_path

	def run_app(self):
		app = web.Application()
		# resolve routing
		# https://stackoverflow.com/questions/34565705/asyncio-and-aiohttp-route-all-urls-paths-to-handler?fbclid=IwAR17Pxyv6grD1csXTOzaLhAhyh2BC48A_3shZDXfWq4dXvNCf58VhHcVQcI
		app.router.add_get("/{tail:.*}.cgi", self.handle_get)
		app.router.add_post("/{tail:.*}.cgi", self.handle_post)
		app.router.add_static("/", path=self.directory_path)
		web.run_app(app, port=self.port)

	@staticmethod
	async def run_cgi_empty(file_path):
		cgi_run_process = await asyncio.create_subprocess_exec(
			str(file_path),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		# https://docs.python.org/3.7/library/subprocess.html#subprocess.Popen.communicate
		try:
			stdout_data, stderr_data = await cgi_run_process.communicate()
		except TimeoutExpired:
			cgi_run_process.kill()
			stdout_data, stderr_data = await cgi_run_process.communicate()

		return stdout_data

	@staticmethod
	async def run_cgi_stdin(file_path, stdin_data):
		cgi_run_process = await asyncio.create_subprocess_exec(
			str(file_path),
			stdin=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		cgi_run_process.stdin.write(stdin_data)
		cgi_run_process.stdin.close()
		# https://docs.python.org/3.7/library/subprocess.html#subprocess.Popen.communicate
		try:
			stdout_data, stderr_data = await cgi_run_process.communicate()
		except TimeoutExpired:
			cgi_run_process.kill()
			stdout_data, stderr_data = await cgi_run_process.communicate()

		return stdout_data

	@staticmethod
	def get_file_path(request, dir_path):
		absolute = dir_path.absolute()
		relative = request.url.relative()

		if absolute is not None and relative is not None:
			return pathlib.Path(str(absolute) + str(relative))

		return None

	@staticmethod
	def handle_response(std_out):
		# https://docs.python.org/3.7/library/mailbox.html#message-objects
		response_message = mailbox.Message(std_out)
		message_headers = response_message.headers
		message_payload = response_message.payload

		response = web.Response(body=message_payload)
		response.headers.add("Content-Type", message_headers.get("Content-Type"))

		return response

	@asyncio.coroutine
	async def handle_get(self, request):
		file_path = self.get_file_path(request, self.directory_path)

		# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
		if not file_path.is_fifo() or file_path is None:
			return web.Response(status=404)

		# value must be string
		os.putenv("CONTENT_LENGTH", str(0))
		self.set_request_meta_variables(request, request.url.relative())
		standard_output = await self.run_cgi_empty(file_path)

		return self.handle_response(standard_output)

	@asyncio.coroutine
	async def handle_post(self, request):
		file_path = self.get_file_path(request, self.directory_path)

		# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
		if not file_path.is_fifo() or file_path is None:
			return web.Response(status=404)

		request_content = await request.read() if request.can_read_body() else None
		# value must be string
		cl_value = str(len(request_content)) if request_content is not None else str(0)
		os.putenv("CONTENT_LENGTH", cl_value)

		self.set_request_meta_variables(request, request.url.relative())

		if request_content is None:
			standard_output = await self.run_cgi_empty(file_path)
		else:
			standard_output = await self.run_cgi_stdin(file_path, request_content)

		return self.handle_response(standard_output)

	def set_request_meta_variables(self, request, file_path_url):
		# init all the variables
		# https://tools.ietf.org/html/rfc3875#section-4.1.1
		# https://docs.python.org/3/library/os.html#os.putenv

		at_value = request.headers.get("Authorization") if request.heades.get("Authorization") is not None else ""
		os.putenv("AUTH_TYPE", at_value)

		ct_value = request.content_type if request.content_type is not None else ""
		os.putenv("CONTENT_TYPE", ct_value)

		os.putenv('GATEWAY_INTERFACE', 'CGI/1.1')
		# specifies a path to be interpreted by the CGI script
		# the path is unquoted and may contains non valid URL characters
		# TODO fix ^^
		os.putenv('PATH_INFO', file_path_url.raw_path)
		os.putenv('PATH_TRANSLATED', file_path_url.path)
		os.putenv('QUERY_STRING', request.query_string)
		os.putenv('REMOTE_ADDR', '127.0.0.1')
		os.putenv('REQUEST_METHOD', request.method)
		os.putenv('SCRIPT_NAME', str(file_path_url))
		os.putenv('SERVER_NAME', '127.0.0.1')
		os.putenv('SERVER_PORT', str(self.port))
		os.putenv('SERVER_PROTOCOL', 'HTTP/1.1')
		os.putenv('SERVER_SOFTWARE', 'aiohttp server')
		os.putenv('REMOTE_HOST', 'NULL')


def run():
	port = int(sys.argv[1])
	directory_path = sys.argv[2]
	# check for os, win should be enough
	# https://docs.python.org/3/library/sys.html#sys.platform
	system_os = sys.platform

	# set loop depending on the system_os
	if system_os == "win32":
		loop = asyncio.ProactorEventLoop()
		asyncio.set_event_loop(loop)

	cgi_request_handler = CgiRequestHandler(port, pathlib.Path(directory_path))
	cgi_request_handler.run_app()


run()
