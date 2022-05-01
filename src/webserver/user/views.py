from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import *

# Create your views here.
def index(request):
    raise Http404("Incorrect usage") 

def user(request, username):
    username = username.lower()
    template = loader.get_template('user/user.html')
    limit = int(request.GET.get('limit', DEFAULT_LIMIT))
    page = int(request.GET.get('page', 0))
    page_count = get_page_count(
        username=username,
        limit=limit
    )
    messages = get_user_messages(
        username=username,
        limit=limit,
        page=page
    )
    context = {
        'username': username,
        'messages': messages,
        'page': page,
        'limit': limit,
        'last_page': page_count-1
    }
    return HttpResponse(template.render(context, request))