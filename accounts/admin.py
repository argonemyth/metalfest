from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

# from django_object_actions import (DjangoObjectActions,
#                                    takes_instance_or_queryset)

from accounts.models import Profile

# class ProfileAdmin(DjangoObjectActions, admin.ModelAdmin):
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter_id', 'facebook_id', 'gender', 'user_image')
    search_fields = ('user__first_tname', 'user__last_name', 'user__email')
    list_filter = ('gender',)
    # ordering = ('name', )

admin.site.unregister(Profile)
admin.site.register(Profile, ProfileAdmin)