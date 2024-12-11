from rest_framework import viewsets
from .models import Category
from .serializers import categorySerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.
class categoryViewSet(viewsets.ModelViewSet):
    serializer_class = categorySerializer
    queryset = Category.objects.all()
    
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = categorySerializer(categories, many=True)  
    return Response(serializer.data)
