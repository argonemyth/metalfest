from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'metalfest.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^metalmap/', include('metalmap.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/', include('userena.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', include('metalmap.urls')),
)
