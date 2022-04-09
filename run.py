from SQLogger import *
import os
import logging

def main():
    logger = setup_logger('retroBot')
    config = retroBot.config.config('config.yaml')
    channels = []
    with open(config['twitch']['channel_file'], 'r') as f:
        for i in f.readlines():
            channels.append(i.strip())
    bot = SQLogger(
        config['postgres']['dbname'], 
        config['postgres']['username'], 
        config['postgres']['password'], 
        config['postgres']['host'], 
        config['postgres']['port'], 
        config['twitch']['username'], 
        config['twitch']['client_id'], 
        config['twitch']['client_secret'], 
        channels
        )
    bot.start()

def setup_logger(logname, logpath=""):
    if not logpath or logpath == "":
        logpath = os.path.join(os.path.dirname(__file__), 'logs')
    else:
        logpath = os.path.abspath(logpath)
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(logpath, logname), when='midnight')
    stream_handler = logging.StreamHandler()
    form = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(form)
    stream_handler.setFormatter(form)
    file_handler.setLevel(logging.INFO)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

if __name__ == "__main__":
    main()