from rest_framework import serializers
from rest_framework.exceptions import ParseError
from festivals.models import Festival, Artist

# Define the models we want to have API end-point
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist 
        fields = ('name',)