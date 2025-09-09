from rest_framework import serializers
from django.db.models import Q

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class CategoryMenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image_url"]

    def get_image_url(self,obj):
        return obj.image.url if obj.image else None

class UpdateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "code", "image", "slug", "description"]