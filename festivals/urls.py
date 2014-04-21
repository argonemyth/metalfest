from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from festivals.views import FestivalJSONList

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'metalfest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^festivals/$', FestivalJSONList.as_view(), name='festival-list'),
    url(r'^$', TemplateView.as_view(template_name="map.html"), name='festival-map'),


)
