from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^npc_corps\.json$', views.npc_corps_json, name='npc_corps'),
    url(r'^skills\.json$', views.skills_json, name='skills'),
    url(r'^ships\.json$', views.ships_json, name='ships'),
    url(r'^favorite/(\d*)', views.favorite, name='favorite'),
    url(r'^unfavorite/(\d*)', views.unfavorite, name='unfavorite'),
]
