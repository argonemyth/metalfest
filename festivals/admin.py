from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from festivals.models import Festival, Artist

def get_lastfm_info(modeladmin, request, queryset):
    for f in queryset:
        if f.lastfm_id is None:
            f.get_lastfm_event_id()

        if f.lastfm_id:
            f.get_event_info()
get_lastfm_info.short_description = _("Get festival info from Last.fm") 

class FestivalAdmin(admin.ModelAdmin):
    """
    Admin class for festivals.
    """
    list_display = ('title', 'start_date', 'end_date', 'location',  'city', 'latitude', 'longitude', 'lastfm_id')
    list_editable = ('start_date', 'end_date', 'location')
    # list_filter = ('city',)
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('slug', )
    ordering = ("start_date", )
    actions = [get_lastfm_info]

admin.site.register(Festival, FestivalAdmin)


class ArtistAdmin(admin.ModelAdmin):
    """
    Admin class for artists.
    """
    list_display = ('name', 'lastfm_url')
    search_fields = ('name', )
    # list_filter = ('genres',)
    ordering = ("name", )

admin.site.register(Artist, ArtistAdmin)
