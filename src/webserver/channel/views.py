from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import get_channel_messages, get_db

def index(request):
    raise Http404("Incorrect usage") 

def channel(request, channel):
    template = loader.get_template('channel/index.html')
    dbs = get_db().list_collection_names()
    if channel.lower() in dbs:
        messages = get_channel_messages(channel)
        return HttpResponse(template.render({'messages': messages, 'channel': channel}, request))
    else:
        raise Http404("Channel not found in database") 
