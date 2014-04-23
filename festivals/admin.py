from django.contrib import admin

from festivals.models import Festival

class FestivalAdmin(admin.ModelAdmin):
    """
    Admin class for blog posts.
    """
    list_display = ('title', 'start_date', 'end_date', 'location',  'city', 'latitude', 'longitude', 'lastfm_id')
    list_editable = ('start_date', 'end_date', 'location')
    # list_filter = ('city',)
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('slug', )
    # date_hierarchy = "date_published"
    ordering = ("start_date", )
    # inlines = [PhotoInline]

    # def save_model(self, request, obj, form, change):
    #     ip = get_ip(request)
    #     if ip == '127.0.0.1':
    #         ip = '41.136.98.140'
    #     if ip:
    #         obj.save(ip)
    #     else:
    #         obj.save()

admin.site.register(Festival, FestivalAdmin)