from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from django_object_actions import (DjangoObjectActions,
                                   takes_instance_or_queryset)

from festivals.models import Festival, Artist
from festivals.forms import FestivalAdminForm

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
    form = FestivalAdminForm
    list_display = ('title', 'start_date', 'end_date', 'location',  'city', 'latitude', 'longitude', 'lastfm_id', 'lineup_info')
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

    def sync_artists(self, request, obj):
        obj.sync_artists()
    sync_artists.label = _("Sync Artists")
    sync_artists.short_description = _("Sync artists field with lineup field") 

    def sync_lineup(self, request, obj):
        obj.sync_lineup()
    sync_lineup.label = _("Sync Lineup")
    sync_lineup.short_description = _("Sync lineup field with artist field") 

    # objectactions = ['get_festival_info']
    objectactions = ('get_festival_info', 'sync_artists', 'sync_lineup')
    actions = ['get_festival_info']

    class Media:
        js = ('/static/bower_components/foundation/js/vendor/jquery.js',)
        
admin.site.register(Festival, FestivalAdmin)


class ArtistAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin class for artists.
    """
    list_display = ('name', 'lastfm_url', 'band_image')
    search_fields = ('name', )
    # list_filter = ('genres',)
    ordering = ('name', )

    @takes_instance_or_queryset
    # def get_artist_info(self, request, obj):
    def get_artist_info(self, request, queryset):
        for a in queryset:
            a.get_info_from_lastfm()
    get_artist_info.label = _("Get Artist Info")
    get_artist_info.short_description = _("Get artist info from last.fm.")

    objectactions = ('get_artist_info', )
    actions = ['get_artist_info']

admin.site.register(Artist, ArtistAdmin)
