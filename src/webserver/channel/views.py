from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import get_channel_messages, get_channels, parse_usernames, DEFAULT_LIMIT

def index(request):
    template = loader.get_template('channel/channel.html')
    return HttpResponse(template.render({'channels': sorted(get_channels())}, request))

def channel(request, channel):
    template = loader.get_template('channel/index.html')
    dbs = get_channels()
    if channel.lower() in dbs:
        username = request.GET.get('username', None)
        filter = {}
        if username:
            filter['username'] = username
        messages = get_channel_messages(
            channel=channel,
            filter=filter,
            limit=int(request.GET.get('limit', DEFAULT_LIMIT)),
            page=int(request.GET.get('page', 0))
        )
        messages = parse_usernames(messages)
        return HttpResponse(template.render({'messages': messages, 'channel': channel}, request))
    else:
        raise Http404("Channel not found in database") 
