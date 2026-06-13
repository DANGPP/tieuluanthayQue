from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Category, Product, Book, Electronic, Fashion, Cosmetic, HealthCare, Office, Food, Sports, Toys, HomeKitchen
from .serializers import (
    CategorySerializer, ProductSerializer, BookSerializer, ElectronicSerializer,
    FashionSerializer, CosmeticSerializer, HealthCareSerializer, OfficeSerializer,
    FoodSerializer, SportsSerializer, ToysSerializer, HomeKitchenSerializer
)

TYPE_SERIALIZER_MAP = {
    'book': (Book, BookSerializer),
    'electronic': (Electronic, ElectronicSerializer),
    'fashion': (Fashion, FashionSerializer),
    'cosmetic': (Cosmetic, CosmeticSerializer),
    'healthcare': (HealthCare, HealthCareSerializer),
    'office': (Office, OfficeSerializer),
    'food': (Food, FoodSerializer),
    'sports': (Sports, SportsSerializer),
    'toys': (Toys, ToysSerializer),
    'homekitchen': (HomeKitchen, HomeKitchenSerializer),
}

def get_product_subtype_details(product):
    for subtype_name, (model_cls, serializer_cls) in TYPE_SERIALIZER_MAP.items():
        # Django multi-table inheritance creates a lowercase relation name on parent
        relation_name = model_cls.__name__.lower()
        if hasattr(product, relation_name):
            sub_obj = getattr(product, relation_name)
            return serializer_cls(sub_obj).data
    return ProductSerializer(product).data

@api_view(['GET', 'POST'])
def category_list_view(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def product_list_view(request):
    if request.method == 'GET':
        category_id = request.query_params.get('category_id')
        search_query = request.query_params.get('search')
        
        products = Product.objects.all()
        if category_id:
            products = products.filter(category_id=category_id)
        if search_query:
            products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
            
        # Serialize polymorphically
        data = [get_product_subtype_details(p) for p in products]
        return Response(data)
        
    elif request.method == 'POST':
        product_type = request.data.get('type')
        if not product_type or product_type not in TYPE_SERIALIZER_MAP:
            return Response(
                {'error': f"Invalid or missing product 'type'. Must be one of: {list(TYPE_SERIALIZER_MAP.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        model_cls, serializer_cls = TYPE_SERIALIZER_MAP[product_type]
        serializer = serializer_cls(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(serializer_cls(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        data = get_product_subtype_details(product)
        return Response(data)
        
    elif request.method == 'PUT':
        # Find if it is a subtype
        matched_type = None
        matched_serializer_cls = ProductSerializer
        matched_obj = product
        
        for subtype_name, (model_cls, serializer_cls) in TYPE_SERIALIZER_MAP.items():
            relation_name = model_cls.__name__.lower()
            if hasattr(product, relation_name):
                matched_type = subtype_name
                matched_serializer_cls = serializer_cls
                matched_obj = getattr(product, relation_name)
                break
                
        serializer = matched_serializer_cls(matched_obj, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            return Response(matched_serializer_cls(updated_product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
