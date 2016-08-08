import simplejson
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from charsearch_app.models import Character, NPC_Corp, Skill, Thread

R_LEVEL = r'level([0-9]+)'
R_FILTER = r'filter([0-9]+)'


@cache_page(60 * 120)
def npc_corps_json(request):
    serialized = serializers.serialize("json", NPC_Corp.objects.all().order_by('name'))
    return HttpResponse(serialized, content_type='application/json')


@cache_page(60 * 120)
def skills_json(request):
    serialized = serializers.serialize("json", Skill.objects.all().order_by('groupName', 'name'))
    return HttpResponse(serialized, content_type='application/json')


@csrf_exempt
def index(request):
    context = {}
    context['threads'] = []
    if len(request.GET) > 0:
        filters = getFilters(request.GET)
    else:
        filters = []
    if filters:
        results = applyFilters(filters)
    else:
        results = Character.objects.all()
    if results > 0:
        threads = Thread.objects.defer('thread_text').select_related('character').filter(
            character__in=results).order_by('-last_update')[:500]
        paginator = Paginator(threads, 25)
        page = request.GET.get('page')
        try:
            threads = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            threads = paginator.page(1)
        except EmptyPage:
            threads = paginator.page(paginator.num_pages)
        context['threads'] = threads
    context['js_filters'] = simplejson.dumps(filters)
    return render(request, 'charsearch_app/home.html', context)


def getFilters(post):
    filters = {}
    for key in post.keys():
        code = key[:2]
        filter_number = key[2:]
        if filter_number not in filters:
            filters[filter_number] = {}
        if code == 'ft':
            filters[filter_number]['filterType'] = post[key]
        elif code == 'cb':
            filters[filter_number]['corporation_box'] = post[key]
        elif code == 'lb':
            filters[filter_number]['level_box'] = int(post[key])
        elif code == 'op':
            filters[filter_number]['operandSelect'] = post[key]
        elif code == 'sa':
            filters[filter_number]['standing_amount'] = float(post[key])
        elif code == 'sc':
            filters[filter_number]['skill_cat'] = int(post[key])
        elif code == 'si':
            filters[filter_number]['sinput'] = post[key]
        elif code == 'sp':
            filters[filter_number]['sp_million'] = int(post[key])
        elif code == 'ti':
            filters[filter_number]['skill_typeID'] = int(post[key])
        elif code == 'so':
            filters[filter_number]['stringOpSelect'] = post[key]
    return [value for (key, value) in sorted(filters.items())]


def applyFilters(filters):
    results = Character.objects.all()
    for f in filters:
        if 'sp_million' in f:
            skillpoints = f['sp_million'] * 1000000
            if f['operandSelect'] == 'eq':
                results = results.filter(total_sp__exact=skillpoints)
            elif f['operandSelect'] == 'ge':
                results = results.filter(total_sp__gte=skillpoints)
            elif f['operandSelect'] == 'le':
                results = results.filter(total_sp__lte=skillpoints)
        elif 'skill_typeID' in f:
            level = f['level_box']
            typeID = f['skill_typeID']
            if f['operandSelect'] == 'eq':
                results = results.filter(skills__skill__typeID=typeID, skills__level=level)
            elif f['operandSelect'] == 'ge':
                results = results.filter(skills__skill__typeID=typeID, skills__level__gte=level)
            elif f['operandSelect'] == 'le':
                results = results.filter(skills__skill__typeID=typeID, skills__level__lte=level)
        elif 'corporation_box' in f:
            req_standing = f['standing_amount']
            corp = f['corporation_box']
            if f['operandSelect'] == 'eq':
                results = results.filter(standings__corp__name=corp, standings__value=req_standing)
            if f['operandSelect'] == 'ge':
                results = results.filter(standings__corp__name=corp, standings__value__gte=req_standing)
            if f['operandSelect'] == 'le':
                results = results.filter(standings__corp__name=corp, standings__value__lte=req_standing)
        elif 'stringOpSelect' in f:
            name = f['sinput']
            if f['stringOpSelect'] == 'eq':
                results = results.filter(name__iexact=name.replace(' ', '_'))
            elif f['stringOpSelect'] == 'cnt':
                results = results.filter(name__icontains=name.replace(' ', '_'))
    return results
