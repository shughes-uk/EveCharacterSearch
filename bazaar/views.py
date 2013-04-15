from django.shortcuts import render,redirect
from bazaar.models import *
from django.utils import simplejson
from django.core import serializers
import datetime , re , ast



R_LEVEL = r'level([0-9]+)'
R_FILTER = r'filter([0-9]+)'

def spambot(request):
    return redirect('http://www.google.com')

def index(request):
    context = {'js_skills': serializers.serialize("json", Skill.objects.all().order_by('groupName','name') ) }
    context['threads'] = []
    if len(request.POST) > 0:
        filters = getFilters(request.POST)
    else:
        filters = request.session.get('filters',default=[])
    if filters:
        results = applyFilters(filters)
        if results > 0:
            for result in results:
                threads = Thread.objects.filter(character=result)
                if len(threads) > 0:
                    context['threads'].append(threads[0])
    request.session['filters'] = filters
    context['threads'].sort(key=lambda x: x.last_update,reverse=True)
    context['js_filters'] = simplejson.dumps(filters)
    return render(request, 'bazaar/home.html', context)

def getFilters(post):
    filters = {}
    for key in post.keys():
        try:
            result = ast.literal_eval(key)
            if type(result) == tuple:
                if filters.has_key(result[1]):
                    filters[result[1]][result[0]] = post[key]
                else:
                    filters[result[1]] = {result[0]:post[key]}
        except ValueError, e:
            if str(e) == 'malformed string':
                continue
            else:
                raise e
    return filters.values()

def applyFilters(filters):
    results = Character.objects.all()
    for f in filters:
        if f.has_key('sp_million'):
            skillpoints = int(f['sp_million']) * 1000000
            if f['operandSelect'] == '==':
                results = results.filter(total_sp__exact=skillpoints)
            elif f['operandSelect'] == '>=':
                results = results.filter(total_sp__gte=skillpoints)
            elif f['operandSelect'] == '<=':
                results = results.filter(total_sp__lte=skillpoints)
        elif f.has_key('skill_typeID'):
            level = int(f['level_box'])
            typeID = int(f['skill_typeID'])
            if f['operandSelect'] == '==':
                results = results.filter(skills__skill__typeID=typeID,skills__level=level)
            elif f['operandSelect'] == '>=':
                results = results.filter(skills__skill__typeID=typeID,skills__level__gte=level)
            elif f['operandSelect'] == '<=':
                results = results.filter(skills__skill__typeID=typeID,skills__level__lte=level)
    return results
