from django.conf.urls import patterns, include, url
# from django.views.generic import TemplateView

from festivals.views import (FestivalJSONList,
                             FesttivalMap)

urlpatterns = patterns('festivals.views',
    url(r'^all/$', FestivalJSONList.as_view(), name='festival-list'),
    url(r'^$', FesttivalMap.as_view(), name='festival-map'),
)
