import retroBot
from pymongo import MongoClient
from threading import Thread
from urllib.parse import quote_plus

class noSQLogger(retroBot.bot.retroBot):

    # dbhosts expected to be array filled with tuples of (IP, port). IP must be filled but port can be None
    def __init__(self, dbname, *args, dbhosts=[('127.0.0.1', None)], dbusername=None, dbpassword=None, dboptions={}, defaultauthdb=None, **kwargs):
        self.dbname = dbname
        self.defaultauthdb = defaultauthdb
        self.dbusername = dbusername
        self.dbpassword = dbpassword
        self.dbhosts = dbhosts
        self.dboptions = dboptions
        self.dbclient = MongoClient(self.get_connection_string())
        if not 'handler' in kwargs:
            kwargs['handler'] = noSQLoggerHandler
        super(noSQLogger, self).__init__(*args, **kwargs)

    def get_connection_string(self):
        out_string = "mongodb://"
        if self.dbusername:
            out_string += f'{quote_plus(self.dbusername)}:{quote_plus(self.dbpassword)}@'
        for i in range(len(self.dbhosts)):
            if i > 0:
                out_string += ','
            out_string += f'{self.dbhosts[i][0]}'
            if self.dbhosts[i][1]:
                out_string += f':{self.dbhosts[i][1]}'
        out_string += '/'
        if self.defaultauthdb:
            out_string += self.defaultauthdb
        if self.dboptions:
            out_string += '?'
            option_count = 0
            for option in self.dboptions:
                if option_count > 0:
                    out_string += '&'
                out_string += f'{option}={self.dboptions[option]}'
                option_count+=1
        return out_string

    def on_pubmsg(self, c, e):
        self.logger.debug(f'Passing message to {e.target[1:]} handler')
        if self.channel_handlers:
            Thread(target=self.channel_handlers[e.target[1:]].on_pubmsg, args=(c, e, )).start()

class noSQLoggerHandler(retroBot.channelHandler):
    
    def __init__(self, channel, parent):
        self.channel = channel
        self.parent = parent
        self.init_db()
        super(noSQLoggerHandler, self).__init__(channel, parent)

    def init_db(self):
        #TODO
        pass

    def on_pubmsg(self, c, e):
        #TODO
        pass
        
class SQLmessage(retroBot.message):

    def to_db_entry(self, channel):
        #TODO
        pass
