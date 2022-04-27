from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from datetime import datetime
from webserver.messages import *

# Create your views here.
def index(request):
    raise Http404("Incorrect usage") 

def user(request, username):
    template = loader.get_template('user/index.html')
    limit = int(request.GET.get('limit', DEFAULT_LIMIT))
    page = int(request.GET.get('page', 0))
    page_count = get_page_count(
        username=username,
        limit=limit
    )
    cursor = get_user_messages(
        username=username,
        limit=limit,
        page=page
    )
    messages = parse_messages(cursor)
    context = {
        'username': username,
        'messages': messages,
        'second_previous_page': page -2,
        'previous_page': page - 1,
        'page': page,
        'next_page': page + 1,
        'second_next_page': page + 2,
        'limit': limit,
        'max_pages': page_count-1
    }
    return HttpResponse(template.render(context, request))