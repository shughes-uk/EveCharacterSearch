# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from bazaar.models import *
import datetime
import re

R_LEVEL = r'level([0-9]+)'
R_FILTER = r'filter([0-9]+)'

def index(request):
    context = {'skills':Skill.objects.all()}
    context['threads'] = []
    if len(request.POST) > 0:
        filterset =  getFilters(request.POST)
        results = Character.objects.all()
        for f in filterset.values():
            results = results.filter(skills__skill__typeID=f['typeid'],skills__level__gte=f['level'])
        if len(results) > 0:
            for result in results:
                thread = Thread.objects.filter(character=result)[0]
                context['threads'].append(thread)
    return render(request, 'bazaar/home.html', context)

def getFilters(post):
    filters = {}
    for key in post:
        result = re.search(R_LEVEL,key)
        if result:
            fnumber = result.group(1)
            if filters.has_key(fnumber):
                filters[fnumber]['level'] = int(post[key])
            else:
                filters[fnumber] = {'level' : int(post[key]) }
        else:
            result = re.search(R_FILTER,key)
            if result:
                fnumber = result.group(1)
                if filters.has_key(fnumber):
                    filters[fnumber]['typeid'] = int(post[key])
                else:
                    filters[fnumber] = { 'typeid' : int(post[key])}
            else:
                continue
    return filters