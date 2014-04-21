from django.core.urlresolvers import resolve
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from django.views.generic import TemplateView

import json

from festivals.views import FestivalJSONList
from festivals.models import Festival
from cities_light.models import City, Region, Country

class HomePageTest(TestCase):

    # def test_root_url_resolves_to_home_page_view(self):
    #     found = resolve('/')
    #     self.assertEqual(found.func, home_page)


    def create_festivals(self):
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
        second_festival.title = "Wacken Open Air"
        second_festival.start_date = "2014-06-20"
        second_festival.end_date = "2014-06-22"
        second_festival.save()

        # Dummy festival 3
        third_festival = Festival()
        third_festival.title = "SWR Barroselas Metalfest XVII"
        third_festival.start_date = "2014-06-20"
        third_festival.end_date = "2014-06-22"
        third_festival.latitude = 41.643485
        third_festival.longitude = -8.686351
        third_festival.save()

    def setUp(self):
        self.create_festivals()
        self.factory = RequestFactory()

    def test_home_page_returns_correct_title(self):
        request = self.factory.get('/')
        view = TemplateView.as_view(template_name="map.html")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'map.html')
        # self.assertTrue(response.content.startswith(b'<html>'))
        # self.assertIn(b'<title>MetalFest</title>', response.content)
        # self.assertTrue(response.content.endswith(b'</html>'))

    def test_festival_list_json_view(self):
        festivals = Festival.objects.all()
        request = self.factory.get('/festivals/')
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

    def create_city(self):
        # create dummy city, region and country for testing
        country = Country(name="United States", continent="NA", phone=1)
        country.save()
        region = Region(name="Texas", country=country)
        region.save(0)
        city = City(name="Amarillo", region=region, country=country)
        city.save()
        return city

    def test_saving_and_retrieving_itmes(self):
        # Dummy festival 1
        first_festival = Festival()
        first_festival.title = "Hellfest"
        first_festival.start_date = "2014-06-20"
        first_festival.end_date = "2014-06-22"
        first_festival.address = "Rue du Champ Louet, 44190 Clisson, France"
        first_festival.save()

        # Dummy festival 2
        second_festival = Festival()
        second_festival.title = "Wacken Open Air"
        second_festival.start_date = "2014-06-20"
        second_festival.end_date = "2014-06-22"
        second_festival.address = "Rue du Champ Louet, 44190 Clisson, France"
        second_festival.save()

        saved_festivals = Festival.objects.all()
        self.assertEqual(saved_festivals.count(), 2)
        first_saved = saved_festivals[0]
        second_saved = saved_festivals[1]
        self.assertEqual(first_saved.title, "Hellfest")
        self.assertEqual(second_saved.title, "Wacken Open Air")

    def test_geocoder(self):
        # Dummy festival
        festival = Festival()
        festival.title = "Hellfest"
        festival.location = "6007 East Amarillo Blvd"
        festival.city = self.create_city() #Amarillo, Texas, United States
        festival.save()
        self.assertEqual(festival.latitude, 35.222553)
        self.assertEqual(festival.longitude, -101.766291)