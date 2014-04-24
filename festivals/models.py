from django.db import models, IntegrityError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
# from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from django.utils.encoding import smart_str

from cities_light.models import City
from geopy import geocoders
from uuslug import uuslug
from taggit.managers import TaggableManager
from bs4 import BeautifulSoup
import urllib2, urllib
import re
import datetime
import json

from festivals import pylast

import logging
logger = logging.getLogger(__name__)

# from django.db.models import Q
#from django.utils.timezone import now


class Artist(models.Model):
    """ This model records the info for a metal band, this model is
        primarily used to cache genre info.
    """
    name = models.CharField(_("name"), max_length=255)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    lastfm_url = models.URLField(_("last.fm URL"), blank=True, null=True)
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

    def get_info_from_lastfm(self, artist=None):
        """
        artist is an Artist object from pylast
        """
        if not artist:
            print "Going to search %s from network." % self.name
            network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                               api_secret = settings.LASTFM_API_SECRET)
            artist = network.get_artist(self.name)

        if artist:
            self.lastfm_url = artist.get_url()
            for tag in artist.get_top_tags():
                self.genres.add(tag)
            self.save()


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

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'latitude': self.latitude,
            'longitude': self.longitude,
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

    def get_event_info(self):
        """Get event info from last.fm"""
        if self.lastfm_id:
            network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                                           api_secret = settings.LASTFM_API_SECRET)
            e = pylast.Event(self.lastfm_id, network)
            venue, location = e.get_venue()
            # print location

            if (self.location is None) and location['name']:
                self.location = location['name']
                street = location.get('steet', '')
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
            if self.lineup is None:
                artists = e.get_artists()
                lineup = []
                for a in artists:
                    name = a.get_name()
                    if name and ( name not in lineup ):
                        lineup.append(name)
                        artist, created = Artist.objects.get_or_create(name=name)
                        if artist.lastfm_url is None:
                            artist.get_info_from_lastfm(a)
                self.lineup = json.dumps(lineup)

            self.save()