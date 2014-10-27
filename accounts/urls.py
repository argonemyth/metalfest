from django.conf.urls import *
from django.contrib.auth import views as auth_views
# from userena.urls import urlpatterns 
# from userena import views as userena_views

# View profiles
urlpatterns = patterns('accounts.views',
    url(r'^$', 'my_profile', name='my_profile'),
)
