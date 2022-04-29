from http.server import BaseHTTPRequestHandler
from noSQLogger import noSQLogger
from logging import getLogger
from urllib.parse import unquote
import json

class TwitchLoggerAPI(BaseHTTPRequestHandler):

    logger = getLogger(__name__)

    def __init__(self, bot: noSQLogger, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    def do_DELETE(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            if not 'channel' in args:
                self.malformed()
            else:
                if self.bot.remove_channel(args['channel']):
                    self.send_response(200)
                else:
                    self.send_response(500)
            

    def do_GET(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            channels = json.dumps({'channels': self.bot.get_channels()})
            self.send_response(200)
            self.wfile.write(channels.encode(encoding='utf_8'))

    def do_PUT(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            if not 'channel' in args:
                self.malformed()
            else:
                if self.bot.add_channel(args['channel']):
                    self.send_response(200)
                else:
                    self.send_response(500)

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
        self.wfile.write('Not found'.encode(encoding='utf_8'))
    
    def malformed(self):
        self.send_response(400)
        self.wfile.write('Bad request'.encode(encoding='utf_8'))

    def respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode(encoding='utf_8'))