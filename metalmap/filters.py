# from django.db.models import Q
# from django.conf import settings
from django.utils.translation import ugettext_lazy as _
# from django.utils import timezone
from django.contrib.admin import SimpleListFilter

# import logging

from metalmap.models import Festival

class YearFilter(SimpleListFilter):
    title = _('year')
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return (('2014', '2014'),
                ('2015', '2015'),
                ('none', _('Not set')),) 

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'none':
            return queryset.filter(start_date__isnull=True)

        return queryset.filter(start_date__year=self.value())