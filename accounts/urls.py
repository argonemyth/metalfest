from django.conf.urls import *
from django.contrib.auth import views as auth_views
# from userena.urls import urlpatterns 
# from userena import views as userena_views
# from accounts.views import SaveMapView


# View profiles
urlpatterns = patterns('accounts.views',
    url(r'^save_map/$', 'save_map', name='save_map'),
    url(r'^$', 'my_profile', name='my_profile'),
)
