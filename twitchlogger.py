import retroBot
import retroBot.config
import psycopg2
from psycopg2 import sql
from time import sleep
from threading import Thread
import json
import os
import logging

def main():
    logger = setup_logger('retroBot')
    config = retroBot.config.config('config.yaml')
    channels = []
    with open(config['twitch']['channel_file'], 'r') as f:
        for i in f.readlines():
            channels.append(i.strip())
    bot = SQLogger(config['postgres']['dbname'], config['postgres']['username'], config['postgres']['password'], config['postgres']['host'], config['postgres']['port'], config['twitch']['username'], config['twitch']['client_id'], config['twitch']['client_secret'], channels, handler=SQLoggerHandler)
    bot.start()

class SQLogger(retroBot.bot.retroBot):

    def __init__(self, dbname, dbusername, dbpassword, dbhost, dbport, *args, **kwargs):
        self.dbname = dbname
        self.dbusername = dbusername
        self.dbpassword = dbpassword
        self.dbhost = dbhost
        self.dbport = dbport
        self.queue = []
        self.queue_process = Thread(target=self.queue_loop, args=(1,), daemon=True)
        super(SQLogger, self).__init__(*args, **kwargs)
        self.queue_process.start()

    def on_pubmsg(self, c, e):
        self.logger.debug(f'Passing message to {e.target[1:]} handler')
        if self.channel_handlers:
            Thread(target=self.channel_handlers[e.target[1:]].on_pubmsg, args=(c, e, )).start()

    def get_conn(self):
        return psycopg2.connect(f"dbname={self.dbname} user={self.dbusername} host={self.dbhost} port={self.dbport} password={self.dbpassword}")
        
    def queue_loop(self, interval = 1):
        while True:
            sleep(interval)
            self.logger.debug(f'Committing {len(self.queue)} entries to database')
            if len(self.queue) > 0:
                conn = self.get_conn()
                cur = conn.cursor()
                temp_queue = self.queue.copy()
                self.queue.clear()
                for s in temp_queue:
                    cur.execute(s[0], s[1])
                conn.commit()
                cur.close()
                conn.close()

class SQLoggerHandler(retroBot.channelHandler):
    
    def __init__(self, channel, parent):
        self.channel = channel
        self.parent = parent
        self.init_db()
        super(SQLoggerHandler, self).__init__(channel, parent)

    def init_db(self):
        conn = self.parent.get_conn()
        cur = conn.cursor()
        cmd = (
            'CREATE TABLE IF NOT EXISTS %s ('
            'channel TEXT NOT NULL, '
            'time TIMESTAMPTZ NOT NULL, '
            'id TEXT NOT NULL, ' 
            'username TEXT NOT NULL, '
            'user_id INTEGER NOT NULL, ' 
            'subscriber BOOL NOT NULL, ' 
            'sub_length SMALLINT, ' 
            'prediction TEXT, ' 
            'badges TEXT[], ' 
            'client_nonce TEXT, ' 
            'color TEXT, ' 
            'emotes TEXT, ' 
            'flags TEXT, ' 
            'mod BOOL NOT NULL, ' 
            'turbo BOOL NOT NULL, ' 
            'content TEXT NOT NULL' 
            ');'
        ) % (f'twitchlogger.chat')
        cur.execute(cmd, ())
        conn.commit()
        cur.close()
        conn.close()

    def on_pubmsg(self, c, e):
        self.parent.queue.append(SQLmessage(e).to_db_entry(self.channel))
        
class SQLmessage(retroBot.message):

    def to_db_entry(self, channel):
        cmd = sql.SQL('INSERT INTO {}.{} (time, channel, id, username, user_id, subscriber, sub_length, prediction, badges, client_nonce, color, emotes, flags, mod, turbo, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);').format(psycopg2.sql.Identifier(f'twitchlogger'), psycopg2.sql.Identifier(f'chat'))
        t = (channel, self.time, self.id, self.username, self.user_id, self.sub, self.sub_length, self.prediction, self.badges, self.client_nonce, self.color, json.dumps(self.emotes), json.dumps(self.flags), self.mod, self.turbo, self.content)
        return cmd, t

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