from django.conf.urls import patterns, include, url
# from django.views.generic import TemplateView

from festivals.views import (FestivalJSONList,
                             FestivalMap,
                             FestivalDetail,
                             ArtistJSONList,
                             ArtistListView,
                             GenreTagListView,
                             FestivalReportErrorView,
                             EventListView)

urlpatterns = patterns('festivals.views',
    url(r'^all/$', FestivalJSONList.as_view(), name='festival-list'),
    url(r'^artists/all/$', ArtistJSONList.as_view(), name='artists-list'),
    url(r'^artists/$', ArtistListView.as_view(), name='artists-search'),
    url(r'^events/$', EventListView.as_view(), name='events-search'),
    url(r'^genres/$', GenreTagListView.as_view(), name='genres-search'),
    url(r'^(?P<slug>[\d\w\-]+)/report/$', FestivalReportErrorView.as_view(),
        name='festival-report'),
    url(r'^(?P<slug>[\d\w\-]+)/$', FestivalDetail.as_view(), name='festival-detail'),
    url(r'^$', FestivalMap.as_view(), name='festival-map'),
)
