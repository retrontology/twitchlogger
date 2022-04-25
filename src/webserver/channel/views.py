from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import *

def index(request):
    template = loader.get_template('channel/channel.html')
    return HttpResponse(template.render({'channels': sorted(get_channels())}, request))

def channel(request, channel):
    template = loader.get_template('channel/index.html')
    dbs = get_channels()
    if channel.lower() in dbs:
        username = request.GET.get('username', None)
        limit = int(request.GET.get('limit', DEFAULT_LIMIT))
        page = int(request.GET.get('page', 0))
        filter = {}
        if username:
            filter['username'] = username
        page_count = get_page_count(filter=filter)
        cursor = get_channel_messages(
            channel=channel,
            filter=filter,
            limit=limit,
            page=page
        )
        messages = []
        for message in cursor:
            message['content'] = parse_usernames(message['content'], channel)
            messages.append(message)
        context = {
            'messages': messages,
            'channel': channel,
            'page': page,
            'limit': limit,
            'page_count': page_count
        }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("Channel not found in database") 
