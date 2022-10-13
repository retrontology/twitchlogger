import retroBot
from pymongo import MongoClient, ASCENDING, DESCENDING
from threading import Thread
from urllib.parse import quote_plus
import datetime

DEFAULT_DB = 'twitch_logger'
MESSAGE_COLLECTION = 'messages'
CHANNEL_COLLECTION = 'channels'
MESSAGE_INDEXES = [
  {
    'keys': [('channel', ASCENDING), ('timestamp', DESCENDING)],
    'name': 'Channel Time Desc',
    'background': False
  },
  {
    'keys': [('username', ASCENDING), ('timestamp', DESCENDING)],
    'name': 'User Time Desc',
    'background': False
  },
  {
    'keys': [('channel', ASCENDING), ('username', ASCENDING), ('timestamp', DESCENDING)],
    'name': 'Channel User Time Desc',
    'background': False
  }
]

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
        self.init_indexes()
        if not 'handler' in kwargs:
            kwargs['handler'] = noSQLoggerHandler
            self.handler = kwargs['handler']
        channels = channels=self.get_channels()
        super(noSQLogger, self).__init__(*args, channels=channels, **kwargs)
    
    def init_indexes(self):
        current_indexes = self.get_messages_collection().list_indexes()
        current_indexes = [index['name'] for index in current_indexes]
        for index in MESSAGE_INDEXES:
            if index['name'] not in current_indexes:
                self.get_messages_collection().create_index(**index)

    def add_channel(self, channel):
        if channel in self.get_channels():
            self.logger.error(f'{channel} already exists in database!')
            return False
        results = self.twitch.get_users(logins=[channel])['data']
        if len(results) == 0:
            self.logger.error(f'{channel} does not exist on twitch!')
            return False
        twitch_id = results[0]['id']
        if self.handler:
            try:
                self.channel_handlers[channel.lower()] = self.handler(channel.lower(), self, ffz=self.ffz, bttv=self.bttv, seventv=self.seventv)
                self.get_channel_collection().insert_one({
                    'channel': channel.lower(),
                    'added': datetime.datetime.now(),
                    'twitch_id': twitch_id,
                    'message_count': 0
                })
                self.join_channel(channel)
                return True
            except Exception as e:
                self.logger.error(e)
                return False
            

    def remove_channel(self, channel):
        if channel.lower() not in self.get_channels():
            self.logger.error(f'{channel} does not exist in database!')
            return False
        if self.handler:
            try:
                test = {}
                self.channel_handlers.pop(channel.lower())
                self.get_channel_collection().delete_one(filter={'channel': channel.lower(),})
                self.connection.part('#' + channel.lower())
                return True
            except Exception as e:
                self.logger.error(e)
                return False
            
    def get_db(self):
        return self.dbclient[self.dbname]
    
    def get_messages_collection(self):
        return self.get_db()[MESSAGE_COLLECTION]
    
    def get_channel_collection(self):
        return self.get_db()[CHANNEL_COLLECTION]
    
    def get_channels(self):
        collection = self.get_channel_collection()
        channels = [entry['channel'] for entry in collection.find()]
        return channels

    def get_connection_string(self):
        out_string = "mongodb://"
        if self.dbusername:
            out_string += f'{quote_plus(self.dbusername)}:{quote_plus(self.dbpassword)}@'
        for i in range(len(self.dbhosts)):
            if i > 0:
                out_string += ','
            out_string += f'{self.dbhosts[i]["host"]}'
            if 'port' in self.dbhosts[i]:
                out_string += f':{self.dbhosts[i]["port"]}'
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
    
    def __init__(self, channel: str, parent: noSQLogger, **kwargs):
        self.channel = channel
        self.parent = parent
        super(noSQLoggerHandler, self).__init__(channel, parent, **kwargs)
        self.update_message_count()
    
    def update_message_count(self):
        count = self.parent.get_messages_collection().count_documents({'channel': self.channel})
        self.parent.get_channel_collection().update_one({'channel': self.channel}, {'$set':{'message_count': count}})

    def on_pubmsg(self, c, e):
        self.parent.get_messages_collection().insert_one(noSQLmessage(e, self.emote_parsers).to_db_entry(self.channel))
        self.parent.get_channel_collection().update_one({'channel': self.channel}, {'$inc': {'message_count': 1}})
        
class noSQLmessage(retroBot.message):

    def to_db_entry(self, channel):
        return {
            'channel': channel,
            'timestamp': self.time,
            'twitch_id': self.id,
            'username': self.username.lower(),
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
            'content': self.content,
            'emotes_ffz': self.emotes_ffz,
            'emotes_bttv': self.emotes_bttv,
            'emotes_seventv': self.emotes_seventv
        }
