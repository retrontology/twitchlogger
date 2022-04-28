from http.server import BaseHTTPRequestHandler
from logging import getLogger
from urllib.parse import unquote
import json

class TwitchLoggerAPI(BaseHTTPRequestHandler):

    logger = getLogger(__name__)

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    def do_DELETE(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            pass

    def do_GET(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            pass

    def do_PUT(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            pass

    def parse_path(self):
        path = unquote(self.path)
        args = path.split('?', 1)
        out_args = {}
        if len(args) > 1:
            path = args[0]
            args = args[1].split('&')
            for arg in args:
                key, value = arg.split('=')
                out_args[key] = value
        return path, out_args

    def not_found(self):
        self.send_response(404)
        self.wfile.write('Not found')

    def respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode(encoding='utf_8'))