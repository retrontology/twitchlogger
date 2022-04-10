from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime


def index(request):
    channel = 'moonmoon'
    template = loader.get_template('channel/index.html')
    messages = [
        {
            'username': 'test1',
            'timestamp': datetime.now(),
            'content': 'Hey :)'
        },
        {
            'username': 'test2',
            'timestamp': datetime.now(),
            'content': 'How\'s it going :)'
        },
        {
            'username': 'test3',
            'timestamp': datetime.now(),
            'content': 'Buddy :)'
        }
    ]
    return HttpResponse(template.render({'messages': messages, 'channel': channel}, request))
