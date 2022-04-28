from noSQLogger import noSQLogger
import retroBot.config
import os
import logging
import logging.handlers

def main():
    logger = setup_logger('retroBot')
    config = retroBot.config.config('config.yaml')
    channels = []
    with open(config['twitch']['channel_file'], 'r') as f:
        for i in f.readlines():
            channels.append(i.strip())
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
    bot.start()

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