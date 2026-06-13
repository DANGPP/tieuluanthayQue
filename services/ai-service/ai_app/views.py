from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserBehavior
from .serializers import UserBehaviorSerializer

@api_view(['GET', 'POST'])
def behavior_list_view(request):
    if request.method == 'GET':
        user_id = request.query_params.get('user_id')
        behaviors = UserBehavior.objects.all()
        if user_id:
            behaviors = behaviors.filter(user_id=user_id)
        return Response(UserBehaviorSerializer(behaviors, many=True).data)
        
    elif request.method == 'POST':
        serializer = UserBehaviorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
