# -*- coding: utf-8 -*-
from django.core.urlresolvers import resolve
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from django.views.generic import TemplateView
from django.conf import settings

from mock import patch, Mock
import json
from decimal import Decimal

from metalmap.views import (FestivalJSONList,
                            FestivalMap,
                            FestivalDetail)
from metalmap.models import Festival, Artist, Gig
from metalmap import pylast

from cities_light.models import City, Region, Country

# Utilities
def create_festivals():
    # Dummy festival 1
    first_festival = Festival()
    first_festival.title = "West Texas Death Fest"
    first_festival.start_date = "2014-06-20"
    first_festival.end_date = "2014-06-22"
    first_festival.location = "Rue du Champ Louet"
    first_festival.latitude = 35.222553
    first_festival.longitude = -101.766291
    first_festival.save()

    # Dummy festival 2
    second_festival = Festival()
    # second_festival.title = "Wacken Open Air"
    second_festival.title = "Sweden Rock Festival"
    second_festival.start_date = "2014-03-20"
    second_festival.end_date = "2014-03-22"
    second_festival.lineup = json.dumps(["Satyricon", "Arch Enemy", "Kreator", "Muse"])
    second_festival.save()

    # Dummy festival 3
    third_festival = Festival()
    third_festival.title = "Eindhoven Metal Meeting"
    third_festival.lastfm_id = "3839143"
    third_festival.start_date = "2014-06-20"
    # third_festival.end_date = "2014-06-22"
    third_festival.latitude = 41.643485
    third_festival.longitude = -8.686351
    third_festival.save()

    # Dummy festival 4
    fourth_festival = Festival()
    fourth_festival.title = "Rock Fest"
    fourth_festival.start_date = "2014-07-20"
    fourth_festival.end_date = "2014-07-22"
    fourth_festival.lineup = json.dumps(["Muse"])
    fourth_festival.save()


def create_artists():
    artists = ["Satyricon", "Arch Enemy", "Kreator", "Muse", "Test"]
    for a_name in artists:
        artist = Artist()
        artist.name = a_name 
        artist.save()
        if a_name == "Satyricon":
            artist.genres.add("black metal")
        if a_name == "Arch Enemy":
            artist.genres.add("melodic death metal")
        if a_name == "Kreator":
            artist.genres.add("thrash metal")
        if a_name == "Muse":
            artist.genres.add("alternative rock")


def create_city():
    # create dummy city, region and country for testing
    country = Country(name="United States", continent="NA", phone=1)
    country.save()
    region = Region(name="Texas", country=country)
    region.save(0)
    city = City(name="Amarillo", region=region, country=country)
    city.save()

    country2 = Country(name="Portugal", continent="EU", phone=2)
    country2.save()
    region2 = Region(name="Viana do Castelo", country=country2)
    region2.save()
    city2 = City(name="Viana do Castelo", region=region2, country=country2)
    city2.save()

    country3 = Country(name="Norway", continent="EU", phone=1, code2="NO")
    country3.save()

    return city


class HomePageTest(TestCase):

    # def test_root_url_resolves_to_home_page_view(self):
    #     found = resolve('/')
    #     self.assertEqual(found.func, home_page)

    def setUp(self):
        create_festivals()
        self.factory = RequestFactory()

    def test_home_page_returns_correct_title(self):
        request = self.factory.get('/')
        # view = TemplateView.as_view(template_name="map.html")
        view = FestivalMap.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'map.html')
        # self.assertTrue(response.content.startswith(b'<html>'))
        # self.assertIn(b'<title>MetalFest</title>', response.content)
        # self.assertTrue(response.content.endswith(b'</html>'))

    def test_festival_list_json_view(self):
        festivals = Festival.objects.all()
        request = self.factory.get('/festivals/all/')
        view = FestivalJSONList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        json_string = response.content
        # print json_string
        data = json.loads(json_string)["festivals"]
        # Shoud not return the festival without lat & log data
        self.assertEqual(len(data), 2)
        # Check data
        self.assertEqual(data[0]['id'], festivals[0].id)
        self.assertEqual(data[1]['id'], festivals[2].id)
        self.assertEqual(data[0]['latitude'], '35.222553')
        self.assertEqual(data[1]['longitude'], '-8.686351')

    def test_festival_detail_view(self):
        festival = Festival.objects.all()[0]
        request = self.factory.get(festival.get_absolute_url())
        view = FestivalDetail.as_view()
        response = view(request, slug=festival.slug).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'metalmap/festival_detail.html')
        self.assertIn(b'Rue du Champ Louet', response.content)


class FestivalModelTest(TestCase):
    def setUp(self):
        create_festivals()
        create_artists()
        create_city()

    def test_saving_and_retrieving_itmes(self):
        saved_festivals = Festival.objects.all()
        self.assertEqual(saved_festivals.count(), 4)
        first_saved = saved_festivals[0]
        second_saved = saved_festivals[1]
        self.assertEqual(first_saved.title, "West Texas Death Fest")
        self.assertEqual(second_saved.title, "Sweden Rock Festival")

    def test_if_past(self):
        first_festival = Festival.objects.get(id=1)
        second_festival = Festival.objects.get(id=2)
        self.assertEqual(first_festival.if_past(), False)
        self.assertEqual(second_festival.if_past(), True)

    def test_geocoder(self):
        # Dummy festival
        festival = Festival.objects.get(id=2) 
        festival.location = "6007 East Amarillo Blvd, Amarillo, Texas"
        festival.country = Country.objects.get(name="United States")  #Amarillo, Texas, United States
        festival.save()
        self.assertEqual(festival.latitude, 35.222553)
        self.assertEqual(festival.longitude, -101.766291)

    """
    You won't be able to find the festival if it's already past.
    def test_get_lastfm_id(self):
        festivals = Festival.objects.all()
        # This festival is not in lastfm
        self.assertEqual(festivals[0].get_lastfm_event_id(), None)
        # The second result test if we enclosed the title in the double
        # quote properly, if not, the id 3602954 will return, which is
        # another festival.
        self.assertEqual(festivals[1].get_lastfm_event_id(), "3616395")
        # Unique festival
        self.assertEqual(festivals[2].get_lastfm_event_id(), "3839143")
    """

    def test_get_event_info(self):
        festival = Festival.objects.get(id=3)
        festival.lastfm_id = "3583454"
        festival.lineup = json.dumps(["Satyricon","arch enemy"])
        festival.get_event_info()
        # should get location and city from last.fm
        self.assertEqual(festival.location, "SWR Fest, Barroselas, Viana do Castelo")
        self.assertEqual(festival.country, Country.objects.get(id=2))
        # lat and lng shouldn't be changed
        self.assertEqual(festival.latitude, Decimal('41.643485'))
        self.assertEqual(festival.longitude, Decimal('-8.686351'))
        self.assertEqual(festival.end_date, "2014-04-26")
        self.assertEqual(festival.facebook_url, "https://www.facebook.com/events/669204766431352/?fref=ts")

    def test_sync_artists(self):
        festival = Festival.objects.get(id=1)
        festival.lineup = json.dumps(["Satyricon","arch enemy"])
        festival.save()
        festival.sync_artists()
        # should be case insensitive
        self.assertEqual(festival.artists.count(), 2)

    def test_sync_lineup(self):
        festival = Festival.objects.get(id=3)
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=3)
        festival.artists.add(artist1)
        festival.artists.add(artist2)
        festival.sync_lineup()
        lineup = festival.get_lineup_display()
        self.assertEqual(lineup, [u'Satyricon', u'Kreator'])
    """
    def test_if_metal_with_current_lineup(self):
        metal_fest = Festival.objects.get(title="Sweden Rock Festival")
        self.assertEqual(metal_fest.lineup, '["Satyricon", "Arch Enemy", "Kreator", "Muse"]')
        self.assertEqual(metal_fest.if_metal(), True)
        self.assertEqual(metal_fest.is_metal, True)
        rock_fest = Festival.objects.get(title="Rock Fest")
        self.assertEqual(rock_fest.lineup, '["Muse"]')
        self.assertEqual(rock_fest.if_metal(), False)
        self.assertEqual(rock_fest.is_metal, False)
    """

    @patch.object(pylast.Event, 'get_artists')
    def test_if_metal_with_no_lineup(self, mock_get_artists):
        network = pylast.LastFMNetwork(api_key = settings.LASTFM_API_KEY,
                                       api_secret = settings.LASTFM_API_SECRET)
        mock_get_artists.return_value=[pylast.Artist('Satyricon', network),
                                       pylast.Artist('Arch Enemy', network),
                                       pylast.Artist('Kreator', network),
                                       pylast.Artist('Test', network),
                                       pylast.Artist('Agalloch', network)]
        fest = Festival.objects.get(title="Eindhoven Metal Meeting")
        self.assertEqual(fest.lineup, None)
        self.assertEqual(fest.if_metal(), True)
        self.assertEqual(fest.is_metal, True)
        # When an existing band has no lineup, it should just skip the band.
        mock_get_artists.return_value=[pylast.Artist('Test', network)]
        self.assertEqual(fest.lineup, None)
        self.assertEqual(fest.if_metal(), None)


class ArtistModelTest(TestCase):
    def setUp(self):
        create_artists()
        create_city()

    def test_saving_and_retrieving_itmes(self):
        saved_artists = Artist.objects.all()
        self.assertEqual(saved_artists.count(), 5)
        first_saved = saved_artists[0]
        second_saved = saved_artists[1]
        self.assertEqual(first_saved.name, "Satyricon")
        self.assertEqual(first_saved.slug, "satyricon")
        self.assertEqual(second_saved.name, "Arch Enemy")
        self.assertEqual(second_saved.slug, "arch-enemy")

    def test_is_metal(self):
        saved_artists = Artist.objects.all()
        self.assertEqual(saved_artists[0].is_metal(), True)
        self.assertEqual(saved_artists[1].is_metal(), True)
        self.assertEqual(saved_artists[2].is_metal(), True)
        self.assertEqual(saved_artists[3].is_metal(), False)
    """
    def test_get_info_from_lastfm(self):
        artist = Artist.objects.get(id=1)
        artist.get_info_from_lastfm()
        self.assertEqual(artist.lastfm_url, "http://www.last.fm/music/satyricon")
        self.assertEqual(artist.genres.count(), 5)
        self.assertEqual(artist.avatar_url_small, "http://userserve-ak.last.fm/serve/64/93039281.jpg")
        self.assertEqual(artist.avatar_url_big, "http://userserve-ak.last.fm/serve/252/93039281.jpg")
        self.assertEqual(artist.mbid,"279d1fd5-9be3-4175-bae6-907fa1ec96fc")

    def test_get_info_from_musicbrainz(self):
        artist = Artist.objects.get(id=1)
        artist.mbid = "279d1fd5-9be3-4175-bae6-907fa1ec96fc"
        normay = Country.objects.get(code2="NO")
        artist.get_info_from_musicbrainz()
        self.assertEqual(artist.country, normay)
        self.assertEqual(artist.official_url, "http://www.satyricon.no/")
        self.assertEqual(artist.ma_url, "http://www.metal-archives.com/bands/Satyricon/341")
        # self.assertEqual(artist.fb_url, None)
        self.assertEqual(artist.fb_url, "https://www.facebook.com/SatyriconOfficial")
        self.assertEqual(artist.twitter_url, "https://twitter.com/satyriconontour")

    def test_update_events_from_lastfm(self):
        pass
    """

class GigModelTest(TestCase):
    def setUp(self):
        create_artists()

    def test_saving_and_retrieving_gigs(self):
        """
        We should able to create an Gig by supplying event name & date.
        """
        event = Gig(title="Cher cher", start_date="2014-06-06")
        event.save()
        saved_event = Gig.objects.all()[0] 
        self.assertEqual(saved_event.slug, "cher-cher")