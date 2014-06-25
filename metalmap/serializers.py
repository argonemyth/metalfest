from rest_framework import serializers
from rest_framework.exceptions import ParseError
from taggit.models import Tag
from cities_light.models import Country
from metalmap.models import Artist, Festival, Gig

# Define the models we want to have API end-point
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist 
        fields = ('name',)


class GenreTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag 
        fields = ('name',)


class ArtistDetailSerializer(serializers.ModelSerializer):
    url = serializers.Field(source='get_external_url')

    class Meta:
        model = Artist
        fields = ('name', 'avatar_url_small', 'url')


class GigSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='country.name')
    artists = ArtistDetailSerializer(many=True)
    class Meta:
        model = Gig
        fields = ('title', 'start_date', 'location', 'country', 'latitude', 'longitude', 'artists')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country 
        fields = ('name',)
