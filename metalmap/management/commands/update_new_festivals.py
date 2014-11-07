from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from optparse import make_option
from metalmap.models import Festival 


class Command(BaseCommand):
    args = '<start_id>'
    help = 'Update all the new metal festivals'

    def handle(self, *args, **options):
        if len(args) > 0:
            start_id = args[0]
        else:
            start_id = 0

        for festival in Festival.objects.filter(Q(id__gt=start_id),
                                                Q(start_date__isnull=True),
                                                ).order_by("id"):
            # self.stdout.write("Checking %s (#%s)" % (festival, festival.id))
            if festival.if_metal_lastfm() == True:
                self.stdout.write("Getting info for festival #%s" % (festival.id))
                try:
                    festival.get_event_info()
                except Exception as e:
                    self.stdout.write("=== Error at getting info: %s" % e)

