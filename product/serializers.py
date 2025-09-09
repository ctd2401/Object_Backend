from rest_framework import serializers
from django.db.models import Q

from .models import *


class ProductVariantSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField()
    class Meta:
        model = ProductVariant
        fields = ['price_diff','variant_name','available']

    def get_variant_name(self,obj):
        return obj.variant.name if obj.variant else None   
class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ("name", "code", "image", "slug", "description","origin_price","available","category_name","variants")

    def get_category_name(self,obj):
        return obj.category.name if obj.category else None

class ProductMenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image_url"]

    def get_image_url(self,obj):
        return obj.image.url if obj.image else None

class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "code", "image", "slug", "description"]