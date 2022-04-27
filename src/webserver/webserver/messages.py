from django.conf import settings
from pymongo import MongoClient
from urllib.parse import quote_plus
from math import ceil

DEFAULT_LIMIT = 50
DEFAULT_FIELDS = [
    'username',
    'timestamp',
    'content',
    'color'
]
DEFAULT_SORT = list({'timestamp': -1}.items())
COLLECTION_NAME = 'messages'
    
def get_channel_messages(channel:str, filter={}, sort=DEFAULT_SORT, fields=DEFAULT_FIELDS, limit=DEFAULT_LIMIT, page=0):
    container = get_db()[COLLECTION_NAME]
    project=get_project(fields)
    filter['channel'] = channel.lower()
    return container.find(
        filter=filter,
        projection=project,
        sort=sort,
        skip=page*limit,
        limit=limit
    )

def get_page_count(channel=None, username=None, filter={}, limit=DEFAULT_LIMIT):
    container = get_db()[COLLECTION_NAME]
    if channel: filter['channel'] = channel
    if username: filter['username'] = channel
    total = container.count_documents(filter=filter)
    return ceil(total / limit)

def get_channels():
    return get_db()[COLLECTION_NAME].distinct('channel')

def get_user_messages(username, channels=None, filter={}, sort=DEFAULT_SORT, fields=DEFAULT_FIELDS, limit=DEFAULT_LIMIT, page=0):
    container = get_db()[COLLECTION_NAME]
    project=get_project(fields)
    filter['username'] = username
    return container.find(
        filter=filter,
        projection=project,
        sort=sort,
        skip=page*limit,
        limit=limit
    )

def get_project(fields):
    project = {}
    project['_id'] = 0
    for field in fields:
        project[field] = 1
    if 'username' in fields:
        project['color'] = 1
    return project

def get_db():
    return get_client()[settings.MONGO_DBNAME]

def get_client():
    return MongoClient(get_connection_string(
        dbhosts=settings.MONGO_HOSTS,
        dbusername=settings.MONGO_USER,
        dbpassword=settings.MONGO_PASS,
        defaultauthdb=settings.MONGO_AUTHDB,
        dboptions=settings.MONGO_OPTIONS
    ))

def get_connection_string(dbhosts, dbusername, dbpassword, defaultauthdb, dboptions):
        out_string = "mongodb://"
        if dbusername:
            out_string += f'{quote_plus(dbusername)}:{quote_plus(dbpassword)}@'
        for i in range(len(dbhosts)):
            if i > 0:
                out_string += ','
            out_string += f'{dbhosts[i][0]}'
            if dbhosts[i][1]:
                out_string += f':{dbhosts[i][1]}'
        out_string += '/'
        if defaultauthdb:
            out_string += defaultauthdb
        if dboptions:
            out_string += '?'
            option_count = 0
            for option in dboptions:
                if option_count > 0:
                    out_string += '&'
                out_string += f'{option}={dboptions[option]}'
                option_count+=1
        return out_string

def parse_messages(cursor):
    messages = []
    for message in cursor:
        message['content'] = parse_usernames(message['content'], message['channel'])
        messages.append(message)
    return messages

def parse_usernames(message: str, channel):
    words = message.split()
    for word in words:
        if word[0] == '@' and len(word) > 1:
            replacement = f'<a style="text-decoration: none;" href="{channel}?username={word[1:]}">{word}</a>'
            message = message.replace(word, replacement, 1)
    return message