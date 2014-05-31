from django import forms 
from django_select2.fields import (AutoModelSelect2Field,
                                   AutoModelSelect2MultipleField)
from cities_light.models import Country, Region, City
# import os

class CitySelect2Field(AutoModelSelect2Field):
    queryset = City.objects
    #search_fields = ['name__icontains', 'display_name__icontains']
    search_fields = ['name__icontains', ]

class CitySelect2MultipleField(AutoModelSelect2MultipleField):
    queryset = City.objects
    search_fields = ['name__icontains', ]

class CountrySelect2Field(AutoModelSelect2Field):
    queryset = Country.objects
    #search_fields = ['name__icontains', 'display_name__icontains']
    search_fields = ['name__icontains', ]