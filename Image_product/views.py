from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import ImageProduct
from establisment.models import Establisment
from product.models import Product
from rest_framework import status
import base64
from django.http import JsonResponse

# Create your views here.
@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def uploadImage(request):
    try:
        id_establisment = request.data.get('id_establisment')
        image = request.FILES.get('image')
        code_product = request.data.get('code_product')
        if not id_establisment or not code_product or not image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageField = image.read()
        
        Product.objects.get(code = code_product)
        if ImageProduct.objects.filter(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(code = code_product)).exists():
            return Response({'error': 'Image already exists'}, status=status.HTTP_400_BAD_REQUEST)
        ImageProduct.objects.create(id_establisment=Establisment.objects.get(id=id_establisment),
                                        id_product=Product.objects.get(code = code_product),
                                        image=imageField)
        return Response({'message': 'Image uploaded successfully'}, status=status.HTTP_201_CREATED)
        
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def getImageProduct(request):
    try:
        code_product = request.query_params.get('code_product')
        id_establisment = request.query_params.get('id_establisment')
        if not code_product or not id_establisment:   
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        image = ImageProduct.objects.get(id_product = Product.objects.get(code = code_product), id_establisment=id_establisment)
        
        imageBase64 = base64.b64encode(image.image).decode('utf-8')
        mime_type = "image/jpeg"
        image_base64_url = f"data:{mime_type};base64,{imageBase64}"
        
        
        return Response({'imagen': image_base64_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
#@permission_classes([IsAuthenticated])
def updateImageProduct(request):
    
    try:
        id_establisment = request.data.get('id_establisment')
        code_product = request.data.get('code_product')
        id_image = request.data.get('id_image')
        image = request.FILES.get('image')
        if not id_establisment or not code_product or not id_image or not image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageField = image.read()

        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(code = code_product), id=id_image)
        imageProduct.image = imageField
        imageProduct.save()
        return Response({'message': 'Image updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
#@permission_classes([IsAuthenticated])
def deleteImageProduct(request):
    try:
        id_establisment = request.query_params.get('id_establisment')
        code_product = request.query_params.get('code_product')
        id_image = request.data.get('id_image')
        if not id_establisment or not code_product or not id_image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(code = code_product), id=id_image)
        imageProduct.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)