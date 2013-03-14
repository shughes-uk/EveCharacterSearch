from django.shortcuts import render,redirect
from bazaar.models import *
from django.utils import simplejson
from django.core import serializers
import datetime , re



R_LEVEL = r'level([0-9]+)'
R_FILTER = r'filter([0-9]+)'

def spambot(request):
    return redirect('http://www.google.com')

def index(request):
    context = {'js_skills': serializers.serialize("json", Skill.objects.all().order_by('groupName','name') ) }
    context['threads'] = []
    if len(request.POST) > 0:
        filterset =  getFilters(request.POST)
        context['filters'] = filterset
        results = Character.objects.all()
        for f in filterset:
            results = results.filter(skills__skill__typeID=f['typeid'],skills__level__gte=f['level'])
        if len(results) > 0:
            for result in results:
                threads = Thread.objects.filter(character=result)
                if len(threads) > 0:
                    context['threads'].append(threads[0])
    context['threads'].sort(key=lambda x: x.last_update,reverse=True)
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
    return filters.values()