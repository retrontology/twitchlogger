from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import get_channel_messages, get_db, DEFAULT_LIMIT

# Create your views here.
def index(request):
    raise Http404("Incorrect usage") 

def user(request, username):
    template = loader.get_template('user/index.html')
    channels = get_db().list_collection_names()
    messages = []
    for channel in channels:
        pass