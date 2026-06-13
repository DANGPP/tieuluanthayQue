from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User, Address
from .serializers import UserSerializer, RegisterSerializer, AddressSerializer, AdminUserSerializer

def get_user_from_request(request):
    user_id = (
        request.headers.get('X-User-Id')
        or request.META.get('HTTP_X_USER_ID')
        or request.query_params.get('user_id')
        or request.GET.get('user_id')
    )
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError):
        return None

def request_role(request):
    return request.headers.get('X-User-Role') or request.query_params.get('role')

def require_admin(request):
    user = get_user_from_request(request)
    if user and user.role == 'admin':
        return user
    if request_role(request) == 'admin':
        return True
    return None

@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def user_me_view(request):
    user = get_user_from_request(request)
    if not user:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(UserSerializer(user).data)

@api_view(['GET'])
def get_user_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_role_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return Response({'id': user.id, 'username': user.username, 'role': user.role, 'is_active': user.is_active})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
def admin_user_list_view(request):
    if not require_admin(request):
        return Response({'error': 'Admin role required'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        role = request.query_params.get('role')
        users = User.objects.all().order_by('id')
        if role:
            users = users.filter(role=role)
        return Response(UserSerializer(users, many=True).data)

    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def admin_user_detail_view(request, user_id):
    if not require_admin(request):
        return Response({'error': 'Admin role required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    if request.method == 'PUT':
        serializer = AdminUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(UserSerializer(updated_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = False
    user.save(update_fields=['is_active'])
    return Response(UserSerializer(user).data)

@api_view(['GET', 'POST'])
def address_list_view(request):
    user = get_user_from_request(request)
    if not user:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'GET':
        addresses = Address.objects.filter(user=user)
        return Response(AddressSerializer(addresses, many=True).data)
        
    elif request.method == 'POST':
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=user, is_default=True).update(is_default=False)
            address = serializer.save(user=user)
            return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def address_detail_view(request, address_id):
    user = get_user_from_request(request)
    if not user:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    try:
        address = Address.objects.get(id=address_id, user=user)
    except Address.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=user, is_default=True).update(is_default=False)
            address = serializer.save()
            return Response(AddressSerializer(address).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        address.delete()
        return Response({'message': 'Address deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
