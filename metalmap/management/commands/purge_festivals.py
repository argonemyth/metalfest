from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from optparse import make_option
from metalmap.models import Festival 


class Command(BaseCommand):
    args = '<start_id>'
    help = 'Purge all the non-metal & past festivals'
    option_list = BaseCommand.option_list + (
        make_option('-n',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Dry run'),
    )

    def handle(self, *args, **options):
        if len(args) > 0:
            start_id = args[0]
        else:
            start_id = 0

        for festival in Festival.objects.filter(Q(id__gt=start_id),
                                                Q(start_date__isnull=True),
                                                ).order_by("id"):
            self.stdout.write("Checking %s (#%s)" % (festival, festival.id))
            if festival.if_past() and ( festival.if_metal_lastfm() == False ):
                if options['dryrun']:
                    self.stdout.write("Deleting %s (#%s)" % (festival, festival.id))
                else:
                    self.stdout.write("Deleting festival #%s" % (festival.id))
                    festival.delete()