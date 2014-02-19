from django.shortcuts import render, redirect
from bazaar.models import *
import ast
import simplejson


R_LEVEL = r'level([0-9]+)'
R_FILTER = r'filter([0-9]+)'


def spambot(request):
    return redirect('http://www.google.com')


def index(request):
    context = {}
    context['threads'] = []
    if len(request.POST) > 0:
        filters = getFilters(request.POST)
    else:
        filters = request.session.get('filters', default=[])
    if filters:
        results = applyFilters(filters)
    else:
        results = Character.objects.all()
    if results > 0:
            context['threads'] = Thread.objects.filter(character__in=results)
    request.session['filters'] = filters
    context['js_filters'] = simplejson.dumps(filters)
    return render(request, 'bazaar/home.html', context)


def getFilters(post):
    filters = {}
    for key in post.keys():
        try:
            result = ast.literal_eval(key)
            if type(result) == tuple:
                if result[1] in filters:
                    filters[result[1]][result[0]] = post[key]
                else:
                    filters[result[1]] = {result[0]: post[key]}
        except ValueError, e:
            if str(e) == 'malformed string':
                continue
            else:
                raise e
    return filters.values()


def applyFilters(filters):
    results = Character.objects.all()
    for f in filters:
        if 'sp_million' in f:
            skillpoints = int(f['sp_million']) * 1000000
            if f['operandSelect'] == '==':
                results = results.filter(total_sp__exact=skillpoints)
            elif f['operandSelect'] == '>=':
                results = results.filter(total_sp__gte=skillpoints)
            elif f['operandSelect'] == '<=':
                results = results.filter(total_sp__lte=skillpoints)
        elif 'skill_typeID' in f:
            level = int(f['level_box'])
            typeID = int(f['skill_typeID'])
            if f['operandSelect'] == '==':
                results = results.filter(
                    skills__skill__typeID=typeID, skills__level=level)
            elif f['operandSelect'] == '>=':
                results = results.filter(
                    skills__skill__typeID=typeID, skills__level__gte=level)
            elif f['operandSelect'] == '<=':
                results = results.filter(
                    skills__skill__typeID=typeID, skills__level__lte=level)
        elif 'corporation_box' in f:
            req_standing = float(f['standing_amount'])
            corp = str(f['corporation_box'])
            if f['operandSelect'] == '==':
                results = results.filter(standings__corp__name=corp, standings__value=req_standing)
            if f['operandSelect'] == '>=':
                results = results.filter(standings__corp__name=corp, standings__value__gte=req_standing)
            if f['operandSelect'] == '<=':
                results = results.filter(standings__corp__name=corp, standings__value__lte=req_standing)
    return results
