from rest_framework import serializers
from .models import Category, Dish, Restaurant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'display_order', 'image']


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Dish
        fields = [
            'id',
            'name',
            'description',
            'price',
            'image',
            'category',
            'category_name',
            'display_order',
            'is_available'
        ]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'image']
