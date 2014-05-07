from django.conf.urls import patterns, include, url
# from django.views.generic import TemplateView

from festivals.views import (FestivalJSONList,
                             FestivalMap,
                             FestivalDetail)

urlpatterns = patterns('festivals.views',
    url(r'^all/$', FestivalJSONList.as_view(), name='festival-list'),
    url(r'^(?P<slug>[\d\w\-]+)/$', FestivalDetail.as_view(), name='festival-detail'),
    url(r'^$', FestivalMap.as_view(), name='festival-map'),
)
