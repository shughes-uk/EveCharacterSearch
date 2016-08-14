import simplejson
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from charsearch_app.models import NPC_Corp, Skill, Thread


@cache_page(60 * 120)
def npc_corps_json(request):
    serialized = serializers.serialize("json", NPC_Corp.objects.all().order_by('name'))
    return HttpResponse(serialized, content_type='application/json')


@cache_page(60 * 120)
def skills_json(request):
    serialized = serializers.serialize("json", Skill.objects.filter(published=True).order_by('groupName', 'name'))
    return HttpResponse(serialized, content_type='application/json')


@csrf_exempt
def favourite(request, thread_id):
    favourites = request.session.get("favourites", [])
    if thread_id not in favourites:
        favourites.append(int(thread_id))
        request.session['favourites'] = favourites
    return HttpResponse()


@csrf_exempt
def unfavourite(request, thread_id):
    favourites = request.session.get("favourites", [])
    if int(thread_id) in favourites:
        favourites.remove(int(thread_id))
        request.session['favourites'] = favourites
    return HttpResponse()


@csrf_exempt
def index(request):
    context = {}
    context['threads'] = []
    if len(request.GET) > 0:
        filters = parseFilters(request.GET)
    else:
        filters = []
    if filters:
        q_objects = generateQObjects(filters)
    else:
        q_objects = []
    if q_objects:
        threads = Thread.objects.filter(blacklisted=False).select_related('character')
        for q in q_objects:
            threads = threads.filter(q)
    else:
        threads = Thread.objects.filter(blacklisted=False).select_related('character').all()
    favourites = request.session.get("favourites", [])
    context['favourites'] = favourites
    threads = threads.order_by('-last_update')
    threads = sorted(threads[:500], key=lambda i: i.id in favourites, reverse=True)
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


def parseFilters(post):
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


def generateQObjects(filters):
    results = []
    for f in filters:
        if 'sp_million' in f:
            skillpoints = f['sp_million'] * 1000000
            if f['operandSelect'] == 'eq':
                results.append(Q(character__total_sp__exact=skillpoints))
                results = results.filter()
            elif f['operandSelect'] == 'ge':
                results.append(Q(character__total_sp__gte=skillpoints))
            elif f['operandSelect'] == 'le':
                results.append(Q(character__total_sp__lte=skillpoints))
        elif 'skill_typeID' in f:
            level = f['level_box']
            typeID = f['skill_typeID']
            if f['operandSelect'] == 'eq':
                results.append(Q(character__skills__typeID=typeID, character__skills__level=level))
            elif f['operandSelect'] == 'ge':
                results.append(Q(character__skills__typeID=typeID, character__skills__level__gte=level))
            elif f['operandSelect'] == 'le':
                results.append(Q(character__skills__typeID=typeID, character__skills__level__lte=level))
        elif 'corporation_box' in f:
            req_standing = f['standing_amount']
            corp = f['corporation_box']
            if f['operandSelect'] == 'eq':
                results.append(Q(character__standings__corp__name=corp, character__standings__value=req_standing))
            if f['operandSelect'] == 'ge':
                results.append(Q(character__standings__corp__name=corp, character__standings__value__gte=req_standing))
            if f['operandSelect'] == 'le':
                results.append(Q(character__standings__corp__name=corp, character__standings__value__lte=req_standing))
        elif 'stringOpSelect' in f:
            name = f['sinput']
            if f['stringOpSelect'] == 'eq':
                results.append(Q(character_name__iexact=name.replace(' ', '_')))
            elif f['stringOpSelect'] == 'cnt':
                results.append(Q(character_name__icontains=name.replace(' ', '_')))
    return results
