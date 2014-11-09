# from django.db.models import Q
# from django.conf import settings
from django.utils.translation import ugettext_lazy as _
# from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from datetime import date
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


class DateFilter(SimpleListFilter):
    title = _('date')
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return (('today', "today's festivals"),
                ('future', 'future festivals'),
                ('past', 'past festivals'))

    def queryset(self, request, queryset):
        today = date.today()
        if not self.value():
            return queryset

        if self.value() == 'today':
            return queryset.filter(start_date=today)

        if self.value() == 'future':
            return queryset.filter(start_date__gt=today)

        if self.value() == 'past':
            return queryset.filter(start_date__lt=today)