from statistics import mode
from rest_framework import serializers

from .models import *

class ScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = "__all__"


class AdsSerializer(serializers.ModelSerializer):
    class Meta:
        model= Ad
        fields = "__all__"
