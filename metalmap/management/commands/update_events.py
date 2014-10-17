from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.utils import timezone
import time

from metalmap.models import Artist 


class Command(BaseCommand):
    help = 'This updates the events of every artist in the db.'
    option_list = BaseCommand.option_list + (
        make_option('-n',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Dry run'),
    )

    def handle(self, *args, **options):
        print "Going to update artist gigs."
        artists = Artist.objects.all().order_by('id')
        self.stdout.write("== Weekly artist update [%s] - %s artists" % (
            timezone.localtime(timezone.now()), artists.count()))

        for artist in artists:
            try:
                artist.update_events_from_lastfm()
                # Pause 5 seconds for each artist update to reduce request
                # ban from musicbrainz
                # time.sleep(5)
            except Exception as e:
                self.stdout.write("++++ Weekly updating for %s (#%s) failed (%s)" % (artist.name, artist.id, e))

        self.stdout.write("==== weekly artist update completed [%s]\n\n" % (
            timezone.localtime(timezone.now()),))