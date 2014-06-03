from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from django_object_actions import (DjangoObjectActions,
                                   takes_instance_or_queryset)

from metalmap.models import Festival, Artist, Gig
from metalmap.forms import FestivalAdminForm

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
    list_display = ('title', 'lineup_info', 'lastfm_id', 'latitude',
                    'longitude', 'location', 'country', 'start_date',
                    'end_date')
    list_editable = ('start_date', 'end_date', 'location')
    # list_filter = ('city',)
    search_fields = ('title', 'description', 'location', 'country__name')
    readonly_fields = ('slug', )
    # ordering = ("start_date", )
    ordering = ("title", "start_date", )
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


class GigAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin class for events.
    """
    list_display = ('title', 'lineup_info', 'lastfm_id', 'lastfm_url',
                    'latitude', 'longitude', 'location', 'country',
                    'start_date')
    # list_editable = ('date', 'end_date', 'location')
    # list_filter = ('city',)
    search_fields = ('title', 'location', 'country__name')
    readonly_fields = ('slug', )
    ordering = ("start_date", 'title')

admin.site.register(Gig, GigAdmin)


class ArtistAdmin(DjangoObjectActions, admin.ModelAdmin):
    """
    Admin class for artists.
    """
    list_display = ('name', 'is_metal', 'official_url', 'lastfm_url', 'mbid', 'band_image')
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

    @takes_instance_or_queryset
    # def get_artist_info(self, request, obj):
    def get_artist_info_musicbrainz(self, request, queryset):
        for a in queryset:
            a.get_info_from_musicbrainz()
    get_artist_info_musicbrainz.label = _("Get Artist Info [MB]")
    get_artist_info_musicbrainz.short_description = _("Get artist info from musicbrainz,\
                                           you need to get mbid from Get\
                                           Artist Info first.")

    @takes_instance_or_queryset
    def update_events(self, request, queryset):
        for a in queryset:
            a.update_events_from_lastfm()
    update_events.label = _("Update Gigs")
    update_events.short_description = _("Update events from last.fm.")

    objectactions = ('get_artist_info', 'get_artist_info_musicbrainz', 'update_events')
    actions = ['get_artist_info', 'get_artist_info_musicbrainz', 'update_events']

admin.site.register(Artist, ArtistAdmin)
