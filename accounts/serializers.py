from rest_framework import serializers
from rest_framework.exceptions import ParseError
from accounts.models import SavedMap

# Define the models we want to have API end-point
class SavedMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedMap 
        fields = ('title', 'map_filters',)
