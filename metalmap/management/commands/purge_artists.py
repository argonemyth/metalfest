from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from metalmap.models import Artist 


class Command(BaseCommand):
    help = 'Purge all the non-metal artists that are not in any festivals'
    option_list = BaseCommand.option_list + (
        make_option('-n',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Dry run'),
    )

    def handle(self, *args, **options):
        for artist in Artist.objects.all():
            if ( not artist.is_metal() ) and ( not artist.festival_count() ):
                if options['dryrun']:
                    self.stdout.write("Deleting %s (#%s)" % (artist.name, artist.id))
                else:
                    self.stdout.write("Deleting %s (#%s)" % (artist.name, artist.id))
                    artist.delete()
            # else:
            #     self.stdout.write("Can't delete %s (#%s) - if metal [%s] - in %s festivals" % (artist.name, artist.id, artist.is_metal(), artist.festival_count()))
