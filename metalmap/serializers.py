from rest_framework import serializers
from rest_framework.exceptions import ParseError
from metalmap.models import Artist, Festival, Gig
from taggit.models import Tag

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
        model = Event
        fields = ('name', 'date', 'location', 'country', 'latitude', 'longitude', 'artists')
