from django.db import models, IntegrityError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
# from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from django.utils.encoding import smart_str

from cities_light.models import City, Country
from geopy import geocoders
from uuslug import uuslug
from taggit.managers import TaggableManager
from bs4 import BeautifulSoup
import urllib2, urllib
import re
import datetime
import json
from datetime import date

from festivals import pylast
from festivals.utils import query_musicbrainz

import logging
logger = logging.getLogger(__name__)

# from django.db.models import Q
#from django.utils.timezone import now


class Artist(models.Model):
    """ This model records the info for a metal band, this model is
        primarily used to cache genre info.
    """
    name = models.CharField(_("name"), db_index=True, max_length=255)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    official_url = models.URLField(_("official URL"), blank=True, null=True)
    lastfm_url = models.URLField(_("last.fm URL"), blank=True, null=True)
    ma_url = models.URLField(_("MetalArchive URL"), blank=True, null=True)
    fb_url = models.URLField(_("facebook URL"), blank=True, null=True)
    twitter_url = models.URLField(_("twitter URL"), blank=True, null=True)
    avatar_url_small = models.URLField(_("artist avatar URL (small)"),
                                       blank=True, null=True)
    avatar_url_big = models.URLField(_("artist avatar URL (big)"),
                                     blank=True, null=True)
    mbid = models.CharField(_("Musicbraiz ID"), max_length=50,
                            blank=True, null=True)
    country = models.ForeignKey('cities_light.Country',
                                verbose_name=_('country'),
                                blank=True, null=True)
    genres = TaggableManager(verbose_name=_("genres"), blank=True, 
                             help_text=_('A comma-separated list of genres'))

    class Meta:
        verbose_name = _('artist')
        verbose_name_plural = _('artists')

    def __unicode__(self):
        return self.name

    def save(self, ip=None, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(Artist, self).save(*args, **kwargs)

    def band_image(self):
        """Display band image if available"""
        if self.avatar_url_small:
            return '<img src="%s">' % self.avatar_url_small
        else:
            return None
    band_image.allow_tags = True

    def serialize(self):
        return {
            'name': self.name
        }

    def get_info_from_lastfm(self, artist=None):
        """
        artist is an Artist object from pylast
        """
        if not artist:
            network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                               api_secret = settings.LASTFM_API_SECRET)
            artist = network.get_artist(self.name)

        if artist:
            save = False
            if not self.lastfm_url:
                self.lastfm_url = artist.get_url()
                save = True

            if not self.mbid:
                self.mbid = artist.get_mbid()
                save = True

            if not self.avatar_url_small:
                self.avatar_url_small = artist.get_cover_image(size=1)
                save = True

            if not self.avatar_url_big:
                self.avatar_url_big = artist.get_cover_image(size=3)
                save = True

            if self.genres.count() == 0:
                top_tags = artist.get_top_tags() 
                for tag in top_tags:
                    self.genres.add(tag)
                self.save()
                return top_tags 

            if save == True:
                # only save lastfm_url
                self.save()
        else:
            return None

    def get_info_from_musicbrainz(self):
        """ We will get the following info from musicbrainz:
            - official_url (typeid: fe33d22f-c3b0-4d68-bd53-a856badf2b15)
            - ma_url ()
            - fb_url
            - twitter_url
            - country
        """
        # Let's try to get mbid if it doesn't exist
        if not self.mbid:
            self.get_info_from_lastfm()

        if self.mbid:
            result = query_musicbrainz(self.mbid)
            urls = result.get("relations", None)
            save = False
            if not self.country:
                c = result["country"]
                if c:
                    try:
                        self.country = Country.objects.get(code2=result["country"])
                        save = True
                    except Exception as e:
                        logger.warning("Got problem finding the country %s" % c)
                        print "=== Warning: Got problem finding the country %s" % c
                        # self.country = None 

            if not self.official_url and urls:
                for r in urls:
                    if r['type-id'] == 'fe33d22f-c3b0-4d68-bd53-a856badf2b15':
                        self.official_url = r["url"]["resource"]
                        save = True
                        break

            if not self.ma_url and urls:
                for r in urls:
                    url = r["url"]["resource"]
                    if 'metal-archives.com' in url:
                        self.ma_url = url
                        save = True
                        break 

            if not self.fb_url and urls:
                for r in urls:
                    url = r["url"]["resource"]
                    if 'facebook.com' in url:
                        self.fb_url = url
                        save = True
                        break 

            if not self.twitter_url and urls:
                for r in urls:
                    url = r["url"]["resource"]
                    if 'twitter.com' in url:
                        self.twitter_url = url
                        save = True
                        break 

            if save == True:
                self.save()

        else:
            return None

    def get_external_url(self):
        """ Return either official, facebook, twitter or ma url """
        if self.official_url:
            return self.official_url
        elif self.fb_url:
            return self.fb_url
        elif self.twitter_url:
            return self.twitter_url
        elif self.ma_url:
            return self.ma_url
        else:
            return None

    def update_events_from_lastfm(self, artist=None):
        """
        artist is an Artist object from pylast
        """
        logger.info("getting events info from %s" % self.name)
        if not artist:
            network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                               api_secret = settings.LASTFM_API_SECRET)
            artist = network.get_artist(self.name)

        if artist:
            upcoming_events = artist.get_upcoming_events()
            for u_event in upcoming_events:
                # Skip the festivals 
                e_id = u_event['id']
                title = u_event['title']
                end_date = u_event['endDate']
                url = u_event['url']

                # make sure it's not a festival 
                if url.startswith("http://www.last.fm/festival/"):
                    festival, created = Festival.objects.get_or_create(lastfm_id=e_id,
                                            defaults={"title": title})
                    if created: 
                        # take too long to get all the info.
                        # festival.get_event_info()
                        logger.info("New festival created: %s (id #%s) " % (title, festival.id) )
                        print "==== New festival created: %s (id #%s) " % (title, festival.id)
                    # else:
                        # print "==== The festival is already created: %s (id #%s) " % (title, festival.id)
                    continue

                # Create our event
                # print "ID: ", e_id
                # print "Title: ", u_event['title']
                # print "Start: ", u_event['startDate']
                event, created = Event.objects.get_or_create(lastfm_id=e_id,
                                    defaults={"name": title,
                                              "date": datetime.datetime.strptime(
                                                            u_event['startDate'],
                                                            '%a, %d %b %Y %H:%M:%S'
                                                       ).strftime('%Y-%m-%d')})
                if created:
                    # print "==== New event created: %s (id #%s) " % (title, event.id)
                    event.start_time = datetime.datetime.strptime(
                                            u_event['startDate'],
                                            '%a, %d %b %Y %H:%M:%S'
                                       ).strftime('%H:%M:%S')

                    venue_id, location = u_event['event'].get_venue()

                    if location['name']:
                        event.location = location['name']
                        street = location.get('street', '')
                        if street:
                            event.location += ", " + street
                        city = location.get('city', '')
                        if city:
                            event.location += ", " + city 

                    if location['country']:
                        # for US cities, it comes with region name like this: 'Baltimore, MD'
                        try:
                            # event.country = Country.objects.get(models.Q(name__iexact=location['country']) | models.Q(alternate_names__icontains=location['country']))
                            event.country = Country.objects.get(name__iexact=location['country'])
                        except Country.DoesNotExist:
                            logger.warning("Country %s can't be find" % (location['country'], ))
                            print "===== Country %s can't be find" % (location['country'], )
                            event.country = None

                        if event.country is None:
                            # let's try again with ulternative name
                            try:
                                event.country = Country.objects.get(alternate_names__icontains=location['country'])
                            except Exception as e: 
                                logger.warning("Can't get country %s - %s" % (location['country'], e))
                                print "===== Can't get country %s - %s" % (location['country'], e)
                                event.country = None

                    if location['lat']:
                        event.latitude = location['lat']

                    if location['lng']:
                        event.longitude = location['lng']

                    event.lastfm_url = url

                    event.save()

                # Update lineup
                artists = u_event['event'].get_artists()
                update = False
                if event.lineup:
                    lineup = json.loads(event.lineup)
                else:
                    lineup = []

                for a in artists:
                    name = a.get_name()
                    if name and ( name not in lineup ):
                        update = True
                        lineup.append(name)
                        artist, created = Artist.objects.get_or_create(name=name)
                        if created:
                            artist.get_info_from_musicbrainz()
                        event.artists.add(artist)

                if update:
                    # print "Going to update lineup"
                    event.lineup = json.dumps(lineup)
                    event.save()


class Event(models.Model):
    """ This model records individual concert of a band."""
    name = models.CharField(_("name"), db_index=True, max_length=255)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    lastfm_id = models.CharField(_("Last.fm event ID"), max_length=100,
                                 null=True, blank=True, unique=True)
    # Time & Location
    date = models.DateField(_("date"), db_index=True)
    start_time = models.TimeField(_("start time"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=300,
                                null=True, blank=True)
    country = models.ForeignKey('cities_light.Country',
                                verbose_name=_('country'),
                                blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)
    computed_address = models.CharField(max_length=255, null=True, blank=True,
                                        help_text=_('The address Google Geocoder used to calculate the geo position'))
    # Lineup info
    artists = models.ManyToManyField(Artist, null=True, blank=True)
    lineup = models.TextField(_('lineup'), null=True, blank=True,
                              help_text=_('Cached value for band lineup, a text field with a json string'))

    # Urls
    ticket_url = models.URLField(_("ticket URL"), blank=True, null=True)
    lastfm_url = models.URLField(_("last.fm URL"), blank=True, null=True)
    facebook_url = models.URLField(_("facebook URL"), blank=True, null=True)

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('date', 'name')

    def __unicode__(self):
        return self.name   

    def get_lineup_display(self):
        return json.loads(self.lineup)

    def get_geo_position(self):
        if (not self.location) or (not self.country):
            return None

        try:
            g = geocoders.GoogleV3()
            address = "%s, %s" % (self.location, self.country)
            self.computed_address, (self.latitude, self.longitude) = g.geocode(smart_str(address),
                                                                     exactly_one=False)[0]
        except Exception as e:
            logger.warning("Can't find the lat, log for %s (%s)" % (address, e))
            return None

    def save(self, ip=None, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        if (self.longitude is None) or (self.latitude is None):
            self.get_geo_position()
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event-detail', args=[self.slug])

    def sync_artists(self):
        """Sync artists field with lineup, might be a temperary method"""
        if self.lineup:
            lineup = json.loads(self.lineup)
            if len(lineup) != self.artists.count():
                for band in lineup:
                    artist = Artist.objects.get(name__iexact=band)
                    self.artists.add(artist)
                    for genre in artist.genres.select_related():
                        self.genres.add(genre)
        return

    def sync_lineup(self):
        """The reverse of sync_artists Sync lineup field with artists,
           might be a temperary method"""
        if self.artists.count() > 0:
            if self.lineup:
                lineup = json.loads(self.lineup)
                # Convert all names in lineup to lowercase for comparison
                lineup_lower = [a.lower() for a in lineup]
            else:
                lineup = []
                lineup_lower = []

            if len(lineup) != self.artists.count():
                for artist in self.artists.select_related():
                    if artist.name.lower() not in lineup_lower:
                        lineup.append(artist.name)
                        for genre in artist.genres.select_related():
                            self.genres.add(genre)
                if lineup:
                    self.lineup = json.dumps(lineup)
                    self.save()
        return

    def lineup_info(self):
        if not self.lineup:
            return "No Lineup"
        else:
            lineup = json.loads(self.lineup)
            if len(lineup) != self.artists.count():
                return "Require Sync"
            else:
                return "Good"


class Festival(models.Model):
    """ This model records the info for a metal festival """
    title = models.CharField(_("title"), max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    description = models.TextField(_("description"), blank=True, null=True)
    start_date = models.DateField(_("start_date"), blank=True, null=True)
    end_date = models.DateField(_("end_date"), blank=True, null=True)
    url = models.URLField(_("URL"), blank=True, null=True)
    # lastfm_url = models.URLField(_("URL"), blank=True, null=True)
    location = models.CharField(_("location"), max_length=300,
                                null=True, blank=True)
    city = models.ForeignKey('cities_light.City',
                             verbose_name=_('city'),
                             blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)
    computed_address = models.CharField(max_length=255, null=True, blank=True,
                                        help_text=_('The address Google Geocoder used to calculate the geo position'))
    artists = models.ManyToManyField(Artist, null=True, blank=True)
    lineup = models.TextField(_('lineup'), null=True, blank=True,
                              help_text=_('Cached value for band lineup, a text field with a json string'))
    genres = TaggableManager(verbose_name=_("genres"), blank=True, 
                             help_text=_('A comma-separated list of genres'))
    lastfm_id = models.CharField(_("Last.fm event ID"), max_length=100,
                                 null=True, blank=True, unique=True)

    class Meta:
        verbose_name = _('festival')
        verbose_name_plural = _('festivals')

    def __unicode__(self):
        return self.title  

    def get_lineup_display(self):
        return json.loads(self.lineup)

    def get_geo_position(self):
        if (not self.location) or (not self.city):
            return None

        try:
            #g = geocoders.GoogleV3(resource='maps')
            g = geocoders.GoogleV3()
            address = "%s, %s" % (self.location, self.city)
            self.computed_address, (self.latitude, self.longitude) = g.geocode(smart_str(address),
                                                                     exactly_one=False)[0]
        except Exception as e:
            logger.warning("Can't find the lat, log for %s (%s)" % (self.location, e))
            return None


    def save(self, ip=None, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        if (self.longitude is None) or (self.latitude is None):
            self.get_geo_position()
        super(Festival, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('festival-detail', args=[self.slug])

    def if_past(self):
        """check if it's a past event"""
        today = date.today()
        if self.end_date and self.end_date < today:
            return True
        return False

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'url': self.url,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'lineup': self.lineup, # json string
            'genres': json.dumps([g.name for g in self.genres.select_related()]),
            'if_past': self.if_past(),
            'detail_url': self.get_absolute_url()
        }

    def get_lastfm_event_id(self):
        """We will make an event search on lastfm."""
        if self.lastfm_id is not None:
            print "Festival %s already got lastfm id (%s)" % (self.title, self.lastfm_id)
            return

        query = {}
        query['q'] = r'"%s"' % self.title.encode("utf-8")
        url_query = urllib.urlencode(query)
        lastfm_url = 'http://www.last.fm/events/search?search=1&by=festival&' + url_query
        # print lastfm_url
        search_result = urllib2.urlopen(lastfm_url).read()
        soup = BeautifulSoup(search_result)
        events = soup.find_all('tr', class_="festival")
        if events:
            event = events[0]
            event_url = event.find("a", class_="url")
            if event_url:
                # Something like this:
                # /festival/3647494+Maryland+Deathfest+XII
                url = event_url.get('href')
                event_id = re.findall(r'\d+', url)[0]
                if event_id:
                    self.lastfm_id = event_id 
                    try:
                        self.save()
                    except IntegrityError:
                        print "Festival %s id already exit - %s" % (self.title, event_id)
                        return None
                    else:
                        return event_id
        else:
            # print "Festival %s not found" % self.title
            return None

    def sync_artists(self):
        """Sync artists field with lineup, might be a temperary method"""
        if self.lineup:
            lineup = json.loads(self.lineup)
            if len(lineup) != self.artists.count():
                for band in lineup:
                    artist = Artist.objects.get(name__iexact=band)
                    self.artists.add(artist)
                    for genre in artist.genres.select_related():
                        self.genres.add(genre)
        return

    def sync_lineup(self):
        """The reverse of sync_artists Sync lineup field with artists,
           might be a temperary method"""
        if self.artists.count() > 0:
            if self.lineup:
                lineup = json.loads(self.lineup)
                # Convert all names in lineup to lowercase for comparison
                lineup_lower = [a.lower() for a in lineup]
            else:
                lineup = []
                lineup_lower = []

            if len(lineup) != self.artists.count():
                for artist in self.artists.select_related():
                    if artist.name.lower() not in lineup_lower:
                        lineup.append(artist.name)
                        for genre in artist.genres.select_related():
                            self.genres.add(genre)
                if lineup:
                    self.lineup = json.dumps(lineup)
                    self.save()
        return


    def lineup_info(self):
        if not self.lineup:
            return "No Lineup"
        else:
            lineup = json.loads(self.lineup)
            if len(lineup) != self.artists.count():
                return "Require Sync"
            else:
                return "Good"


    def get_event_info(self):
        """Get event info from last.fm"""
        if self.lastfm_id:
            network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                                           api_secret = settings.LASTFM_API_SECRET)
            e = pylast.Event(self.lastfm_id, network)
            venue, location = e.get_venue()
            # print location

            if (not self.location) and location['name']:
                self.location = location['name']
                street = location.get('street', '')
                if street:
                    self.location += ", " + street

            if (self.city is None) and (location['city'] and location['country']):
                # for US cities, it comes with region name like this: 'Baltimore, MD'
                city_info = location['city'].split(',')
                if city_info == 2:
                    city_name = city_info[0].strip()
                    region_name = city_info[1].strip()
                    try:
                        city = City.objects.get(models.Q(name__iexact = city_name),
                                                models.Q(region__alternate_names__icontains=region_name),
                                                models.Q(country__name__iexact=location['country']))
                    except City.DoesNotExist:
                        city = None
                else:
                    city_name = city_info[0].strip()
                    try:
                        city = City.objects.get(models.Q(name__iexact = city_name),
                                                models.Q(country__name__iexact=location['country']))
                    except City.DoesNotExist:
                        city = None

                if city:
                    self.city = city

            if (self.latitude is None) and location['lat']:
                self.latitude = location['lat']

            if (self.longitude is None) and location['lng']:
                self.longitude = location['lng']

            if self.start_date is None:
                # The date format is this: Wed, 23 Apr 2014 16:36:01
                start_d = e.get_start_date()
                if start_d:
                    self.start_date = datetime.datetime.strptime(
                                        start_d, '%a, %d %b %Y %H:%M:%S'
                                      ).strftime('%Y-%m-%d')

            if self.end_date is None:
                # If there is no end date, it's the same as start date
                end_d = e.get_end_date()
                if not end_d: 
                    end_d = e.get_start_date()

                if end_d:
                    self.end_date = datetime.datetime.strptime(
                                        end_d, '%a, %d %b %Y %H:%M:%S'
                                      ).strftime('%Y-%m-%d')

            # Get Lineup
            if not self.lineup:
                artists = e.get_artists()
                lineup = []
                for a in artists:
                    name = a.get_name()
                    if name and ( name not in lineup ):
                        lineup.append(name)
                        artist, created = Artist.objects.get_or_create(name=name)
                        # Need to add it to artists as well
                        self.artists.add(artist)
                        if created or ( artist.genres.count() == 0 ):
                            # Getting from last.fm
                            top_tags = artist.get_info_from_lastfm(a)
                        else:
                            # Getting the existing tags from artist.
                            top_tags = artist.genres.all()

                        if top_tags:
                            for tag in top_tags:
                                self.genres.add(tag)

                self.lineup = json.dumps(lineup)

            self.save()