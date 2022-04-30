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
                    result = {
                        'result': True
                    }
                    self.respond(200, json.dumps(result))
                else:
                    result = {
                        'result': False
                    }
                    self.respond(500, json.dumps(result))
            

    def do_GET(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            channels = json.dumps({'channels': self.bot.get_channels()})
            self.respond(200, channels)
            

    def do_PUT(self):
        path, args = self.parse_path()
        if path != '/channel':
            self.not_found()
        else:
            if not 'channel' in args:
                self.malformed()
            else:
                if self.bot.add_channel(args['channel']):
                    result = {
                        'result': True
                    }
                    self.respond(200, json.dumps(result))
                else:
                    result = {
                        'result': False
                    }
                    self.respond(500, json.dumps(result))

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

    def respond(self, code, message=None):
        self.send_response(200)
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(message.encode())

    def not_found(self):
        self.respond(404, 'Not found')
    
    def malformed(self):
        self.respond(400, 'Bad request')
