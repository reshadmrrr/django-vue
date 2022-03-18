from attr import field
from rest_framework import serializers

from .models import Product, ProductVariant, ProductVariantPrice


class ProductVariantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductVariant
        fields = ('variant_title', 'variant')
        # fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ('id', 'title', 'sku', 'description')
        # fields = "__all__"

class ProductVariantPriceSerializer(serializers.ModelSerializer):
    product_variant_one = serializers.SlugRelatedField(read_only=True, slug_field='variant_title')
    product_variant_two = serializers.SlugRelatedField(read_only=True, slug_field='variant_title')
    product_variant_three = serializers.SlugRelatedField(read_only=True, slug_field='variant_title')
    class Meta:
        model = ProductVariantPrice
        fields = ('product_variant_one', 'product_variant_two', 'product_variant_three', 'price', 'stock')
        # fields = "__all__"
        