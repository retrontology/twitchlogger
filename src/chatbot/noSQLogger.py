import retroBot
from pymongo import MongoClient
from threading import Thread
from urllib.parse import quote_plus

DEFAULT_DB = 'twitchlogger'
MESSAGE_COLLECTION = 'messages'
CHANNEL_COLLECTION = 'channels'

class noSQLogger(retroBot.bot.retroBot):

    # dbhosts expected to be array filled with tuples of (IP, port). IP must be filled but port can be None
    def __init__(self, *args, dbhosts=[('127.0.0.1', None)], dbusername=None, dbpassword=None, dboptions={}, defaultauthdb=None, dbname=DEFAULT_DB, **kwargs):
        self.dbname = dbname
        self.defaultauthdb = defaultauthdb
        self.dbusername = dbusername
        self.dbpassword = dbpassword
        self.dbhosts = dbhosts
        self.dboptions = dboptions
        self.dbclient = MongoClient(self.get_connection_string())
        if not 'handler' in kwargs:
            kwargs['handler'] = noSQLoggerHandler
        super(noSQLogger, self).__init__(self.get_channels(), *args, **kwargs)
    
    def add_channel(self, channel):
        self.channels()
        if self.handler:
            try:
                self.channel_handlers[channel.lower()] = self.handler(channel.lower(), self)
            except Exception as e:
                self.logger.error(e)

    def remove_channel(self, channel):
        pass
    
    def get_db(self):
        return self.dbclient[self.dbname]
    
    def get_messages_collection(self):
        return self.get_db()[MESSAGE_COLLECTION]
    
    def get_channel_collection(self):
        return self.get_db()[CHANNEL_COLLECTION]
    
    def get_channels(self):
        collection = self.get_channel_collection()
        channels = [entry['channel'] for entry in collection.find()]

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
    
    def __init__(self, channel: str, parent: noSQLogger):
        self.channel = channel
        self.parent = parent
        super(noSQLoggerHandler, self).__init__(channel, parent)

    def on_pubmsg(self, c, e):
        self.parent.get_messages_collection().insert_one(noSQLmessage(e).to_db_entry(self.channel))
        
class noSQLmessage(retroBot.message):

    def to_db_entry(self, channel):
        return {
            'channel': channel,
            'timestamp': self.time,
            'twitch_id': self.id,
            'username': self.username,
            'user_id': self.user_id,
            'subscription': self.sub,
            'sub_length': self.sub_length,
            'prediction': self.prediction,
            'badges': self.badges,
            'client_nonce': self.client_nonce,
            'color': self.color,
            'emotes': self.emotes,
            'flags': self.flags,
            'mod': self.mod,
            'turbo': self.turbo,
            'content': self.content
        }
