from django.conf import settings
from pymongo import MongoClient
from urllib.parse import quote_plus
from math import ceil

DEFAULT_LIMIT = 50
DEFAULT_FIELDS = [
    'channel',
    'username',
    'timestamp',
    'content',
    'color'
]
DEFAULT_SORT = list({'timestamp': -1}.items())
MESSAGE_COLLECTION = 'messages'
TIMESTAMP_FORMAT = '%H:%M:%S %m/%d/%y'
    
def get_channel_messages(channel:str, filter={}, sort=DEFAULT_SORT, fields=DEFAULT_FIELDS, limit=DEFAULT_LIMIT, page=0):
    container = get_db()[MESSAGE_COLLECTION]
    project=get_project(fields)
    filter['channel'] = channel.lower()
    cursor = container.find(
        filter=filter,
        projection=project,
        sort=sort,
        skip=page*limit,
        limit=limit
    )
    return parse_messages(cursor)

def get_page_count(channel=None, username=None, filter={}, limit=DEFAULT_LIMIT):
    container = get_db()[MESSAGE_COLLECTION]
    if channel: filter['channel'] = channel
    if username: filter['username'] = username
    total = container.count_documents(filter=filter)
    return ceil(total / limit)

def get_channels():
    return get_db()[MESSAGE_COLLECTION].distinct('channel')

def get_user_color(username):
    username = username.lower()
    collection = get_db()[MESSAGE_COLLECTION]
    filter={
        'username': 'retrontology'
    }
    project={
        '_id': 0, 
        'color': 1
    }
    limit=1
    count = collection.count_documents(
        filter=filter,
        limit=limit
    )
    if count != 1:
        return None
    color = next(collection.find(
        filter=filter,
        projection=project,
        limit=limit
    ))['color']
    return color

def get_user_messages(username, channels=None, filter={}, sort=DEFAULT_SORT, fields=DEFAULT_FIELDS, limit=DEFAULT_LIMIT, page=0):
    container = get_db()[MESSAGE_COLLECTION]
    project=get_project(fields)
    filter['username'] = username
    cursor = container.find(
        filter=filter,
        projection=project,
        sort=sort,
        skip=page*limit,
        limit=limit
    )
    return parse_messages(cursor)

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
        message = parse_usernames(message)
        message = parse_timestamp(message)
        messages.append(message)
    return messages

def parse_timestamp(message):
    message['timestamp'] = message['timestamp'].strftime(TIMESTAMP_FORMAT)
    return message

def parse_usernames(message):
    words = message['content'].split()
    for word in words:
        if word[0] == '@' and len(word) > 1:
            target_user = word[1:]
            channel = message['channel']
            color = get_user_color(target_user)
            if color:
                color = f' color: {color};'
            else:
                color = ''
            replacement = f'<a style="text-decoration: none;{color}" href="/channel/{channel}?username={target_user}">{word}</a>'
            message['content'] = message['content'].replace(word, replacement, 1)
    return message