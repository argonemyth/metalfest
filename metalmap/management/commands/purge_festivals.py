from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from metalmap.models import Festival 


class Command(BaseCommand):
    help = 'Purge all the non-metal & past festivals'
    option_list = BaseCommand.option_list + (
        make_option('-n',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Dry run'),
    )

    def handle(self, *args, **options):
        for festival in Festival.objects.filter(start_date__isnull=True).order_by("id"):
            if festival.if_past() and ( festival.if_metal_lastfm() == False ):
                if options['dryrun']:
                    self.stdout.write("Deleting %s (#%s)" % (festival, festival.id))
                else:
                    self.stdout.write("Deleting %s (#%s)" % (festival, festival.id))
                    festival.delete()