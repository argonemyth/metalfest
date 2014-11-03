from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

# from django_object_actions import (DjangoObjectActions,
#                                    takes_instance_or_queryset)

from accounts.models import Profile, SavedMap

class SavedMapInline(admin.TabularInline):
    model = SavedMap
    extra = 0

# class ProfileAdmin(DjangoObjectActions, admin.ModelAdmin):
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter_id', 'facebook_id', 'gender', 'user_image')
    search_fields = ('user__first_tname', 'user__last_name', 'user__email')
    list_filter = ('gender',)
    inlines = [SavedMapInline]
    # ordering = ('name', )

class SavedMapAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'map_filters', 'created_at')
    list_filter = ('profile', )

admin.site.unregister(Profile)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SavedMap, SavedMapAdmin)
