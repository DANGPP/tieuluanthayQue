from rest_framework import serializers
from .models import Category, Product, Book, Electronic, Fashion, Cosmetic, HealthCare, Office, Food, Sports, Toys, HomeKitchen

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'created_at', 'updated_at']

class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Book
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'author', 'publisher', 'isbn', 'page', 'language', 'created_at', 'updated_at']

class ElectronicSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Electronic
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'warranty', 'model', 'power', 'created_at', 'updated_at']

class FashionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Fashion
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'size', 'color', 'material', 'gender', 'created_at', 'updated_at']

class CosmeticSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Cosmetic
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'skin_type', 'expiry_date', 'origin', 'created_at', 'updated_at']

class HealthCareSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = HealthCare
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'ingredient', 'expiry_date', 'usage', 'created_at', 'updated_at']

class OfficeSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Office
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'material', 'color', 'size', 'created_at', 'updated_at']

class FoodSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Food
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'weight', 'expiry_date', 'origin', 'created_at', 'updated_at']

class SportsSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Sports
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'size', 'weight', 'sport_type', 'created_at', 'updated_at']

class ToysSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Toys
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'age_range', 'material', 'player_count', 'created_at', 'updated_at']

class HomeKitchenSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = HomeKitchen
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'brand', 'material', 'capacity', 'warranty', 'created_at', 'updated_at']
