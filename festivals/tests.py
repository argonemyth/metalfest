from django.core.urlresolvers import resolve
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from django.views.generic import TemplateView

import json
from decimal import Decimal

from festivals.views import FestivalJSONList, FesttivalMap
from festivals.models import Festival, Artist
from cities_light.models import City, Region, Country

# Utilities
def create_festivals():
    # Dummy festival 1
    first_festival = Festival()
    first_festival.title = "West Texas Death Fest"
    first_festival.start_date = "2014-06-20"
    first_festival.end_date = "2014-06-22"
    first_festival.address = "Rue du Champ Louet"
    first_festival.latitude = 35.222553
    first_festival.longitude = -101.766291
    first_festival.save()

    # Dummy festival 2
    second_festival = Festival()
    # second_festival.title = "Wacken Open Air"
    second_festival.title = "Sweden Rock Festival"
    second_festival.start_date = "2014-06-20"
    second_festival.end_date = "2014-06-22"
    second_festival.save()

    # Dummy festival 3
    third_festival = Festival()
    third_festival.title = "SWR Barroselas Metalfest XVII"
    third_festival.start_date = "2014-06-20"
    # third_festival.end_date = "2014-06-22"
    third_festival.latitude = 41.643485
    third_festival.longitude = -8.686351
    third_festival.save()


def create_artists():
    artists = ["Satyricon", "Arch Enemy"]
    for a_name in artists:
        artist = Artist()
        artist.name = a_name 
        artist.save()


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
        view = FesttivalMap.as_view()
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


class FestivalModelTest(TestCase):
    def setUp(self):
        create_festivals()
        self.city = create_city()

    def test_saving_and_retrieving_itmes(self):
        saved_festivals = Festival.objects.all()
        self.assertEqual(saved_festivals.count(), 3)
        first_saved = saved_festivals[0]
        second_saved = saved_festivals[1]
        self.assertEqual(first_saved.title, "West Texas Death Fest")
        self.assertEqual(second_saved.title, "Sweden Rock Festival")

    def test_geocoder(self):
        # Dummy festival
        festival = Festival.objects.get(id=2) 
        festival.location = "6007 East Amarillo Blvd"
        festival.city = self.city #Amarillo, Texas, United States
        festival.save()
        self.assertEqual(festival.latitude, 35.222553)
        self.assertEqual(festival.longitude, -101.766291)

    def test_get_lastfm_id(self):
        festivals = Festival.objects.all()
        # This festival is not in lastfm
        self.assertEqual(festivals[0].get_lastfm_event_id(), None)
        # The second result test if we enclosed the title in the double
        # quote properly, if not, the id 3602954 will return, which is
        # another festival.
        self.assertEqual(festivals[1].get_lastfm_event_id(), "3616395")
        # Unique festival
        self.assertEqual(festivals[2].get_lastfm_event_id(), "3583454")

    def test_get_event_info(self):
        festival = Festival.objects.get(id=3)
        festival.lastfm_id = "3583454"
        festival.get_event_info()
        # should get location and city from last.fm
        self.assertEqual(festival.location, "SWR Fest, Barroselas")
        self.assertEqual(festival.city, City.objects.get(id=2))
        # lat and lng shouldn't be changed
        self.assertEqual(festival.latitude, Decimal('41.643485'))
        self.assertEqual(festival.longitude, Decimal('-8.686351'))
        self.assertEqual(festival.end_date, "2014-04-26")


class ArtistModelTest(TestCase):
    def setUp(self):
        create_artists()

    def test_saving_and_retrieving_itmes(self):
        saved_artists = Artist.objects.all()
        self.assertEqual(saved_artists.count(), 2)
        first_saved = saved_artists[0]
        second_saved = saved_artists[1]
        self.assertEqual(first_saved.name, "Satyricon")
        self.assertEqual(first_saved.slug, "satyricon")
        self.assertEqual(second_saved.name, "Arch Enemy")
        self.assertEqual(second_saved.slug, "arch-enemy")
