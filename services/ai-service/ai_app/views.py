from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import KnowledgeBaseEntry, UserBehavior
from .serializers import KnowledgeBaseEntrySerializer, UserBehaviorSerializer

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


def _knowledge_queryset(params):
    queryset = KnowledgeBaseEntry.objects.filter(is_active=True)
    category = params.get('category')
    intent = params.get('intent')
    source_type = params.get('source_type')
    query = params.get('q') or params.get('query')

    if category:
        queryset = queryset.filter(category__iexact=category)
    if intent:
        queryset = queryset.filter(intent__iexact=intent)
    if source_type:
        queryset = queryset.filter(source_type__iexact=source_type)
    if query:
        terms = [term.strip() for term in query.replace(',', ' ').split() if term.strip()]
        if terms:
            condition = Q()
            for term in terms:
                condition |= (
                    Q(title__icontains=term)
                    | Q(content__icontains=term)
                    | Q(category__icontains=term)
                    | Q(intent__icontains=term)
                    | Q(tags__icontains=term)
                )
            queryset = queryset.filter(condition)

    return queryset.distinct().order_by('-priority', 'title')


@api_view(['GET', 'POST'])
def knowledge_base_list_view(request):
    if request.method == 'GET':
        queryset = _knowledge_queryset(request.query_params)
        limit = int(request.query_params.get('limit', 50))
        return Response(KnowledgeBaseEntrySerializer(queryset[:limit], many=True).data)

    serializer = KnowledgeBaseEntrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def knowledge_base_detail_view(request, entry_id):
    try:
        entry = KnowledgeBaseEntry.objects.get(id=entry_id, is_active=True)
    except KnowledgeBaseEntry.DoesNotExist:
        return Response({'error': 'Knowledge base entry not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(KnowledgeBaseEntrySerializer(entry).data)


@api_view(['GET'])
def knowledge_search_view(request):
    queryset = _knowledge_queryset(request.query_params)
    limit = int(request.query_params.get('limit', 10))
    results = KnowledgeBaseEntrySerializer(queryset[:limit], many=True).data
    return Response({
        'query': request.query_params.get('q') or request.query_params.get('query') or '',
        'count': len(results),
        'results': results,
    })


@api_view(['GET'])
def rag_context_view(request):
    queryset = _knowledge_queryset(request.query_params)
    limit = int(request.query_params.get('limit', 5))
    entries = list(queryset[:limit])
    context_blocks = [
        f"[{entry.source_type.upper()}] {entry.title}\n"
        f"Category: {entry.category or 'general'} | Intent: {entry.intent or 'general'}\n"
        f"{entry.content}"
        for entry in entries
    ]
    return Response({
        'query': request.query_params.get('q') or request.query_params.get('query') or '',
        'context': '\n\n---\n\n'.join(context_blocks),
        'entries': KnowledgeBaseEntrySerializer(entries, many=True).data,
    })
