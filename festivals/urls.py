from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from festivals.views import FestivalJSONList

urlpatterns = patterns('festivals.views',
    url(r'^all/$', FestivalJSONList.as_view(), name='festival-list'),
    url(r'^$', TemplateView.as_view(template_name="map.html"), name='festival-map'),
)
