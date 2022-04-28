from noSQLogger import noSQLogger
from functools import partial
from api import TwitchLoggerAPI
import retroBot.config
import os
import logging
import logging.handlers
from http.server import ThreadingHTTPServer
from threading import Thread

def main():
    logger = setup_logger('retroBot')
    config = retroBot.config.config('config.yaml')
    #bot, bot_thread = setup_bot(config)
    bot = None
    setup_api(bot, config['api'])

def setup_api(bot, config):
    api_handler = partial(TwitchLoggerAPI, bot)
    api_server = ThreadingHTTPServer((config['host'], config['port']), api_handler)
    api_server.serve_forever()

def setup_bot(config):
    bot = noSQLogger(
        config['twitch']['username'], 
        config['twitch']['client_id'], 
        config['twitch']['client_secret'],
        dbhosts=config['mongo']['hosts'],
        dbusername=config['mongo']['username'],
        dbpassword=config['mongo']['password'],
        dboptions=config['mongo']['options'],
        defaultauthdb=config['mongo']['authdb'],
        dbname=config['mongo']['dbname']
    )
    bot_thread = Thread(target=bot.start, daemon=True).start()
    return bot, bot_thread

def setup_logger(logprefix, logname=None, logpath=""):
    if not logpath or logpath == "":
        logpath = os.path.join(os.path.dirname(__file__), 'logs')
    else:
        logpath = os.path.abspath(logpath)
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(logpath, logprefix), when='midnight')
    stream_handler = logging.StreamHandler()
    form = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(form)
    stream_handler.setFormatter(form)
    file_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

if __name__ == "__main__":
    main()