from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from django_object_actions import (DjangoObjectActions,
                                   takes_instance_or_queryset)

from festivals.models import Festival, Artist

# def get_lastfm_info(modeladmin, request, queryset):
#     for f in queryset:
#         if f.lastfm_id is None:
#             f.get_lastfm_event_id()

#         if f.lastfm_id:
#             f.get_event_info()
# get_lastfm_info.short_description = _("Get festival info from Last.fm") 


class FestivalAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin class for festivals.
    """
    list_display = ('title', 'start_date', 'end_date', 'location',  'city', 'latitude', 'longitude', 'lastfm_id')
    list_editable = ('start_date', 'end_date', 'location')
    # list_filter = ('city',)
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('slug', )
    ordering = ("start_date", )
    # actions = [get_lastfm_info]

    @takes_instance_or_queryset
    def get_festival_info(self, request, queryset):
        for f in queryset:
            if not f.lastfm_id:
                f.get_lastfm_event_id()

            if f.lastfm_id:
                f.get_event_info()
    get_festival_info.label = _("Get Festival Info")
    get_festival_info.short_description = _("Get festival info from Last.fm") 
    # objectactions = ['get_festival_info']
    objectactions = ('get_festival_info', )
    actions = ['get_festival_info']
admin.site.register(Festival, FestivalAdmin)


class ArtistAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin class for artists.
    """
    list_display = ('name', 'lastfm_url')
    search_fields = ('name', )
    # list_filter = ('genres',)
    ordering = ('name', )

    def get_artist_info(self, request, obj):
        obj.get_info_from_lastfm()
    get_artist_info.label = _("Get Artist Info")
    get_artist_info.short_description = _("Get artist info from last.fm.")

    objectactions = ('get_artist_info', )

admin.site.register(Artist, ArtistAdmin)
