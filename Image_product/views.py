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
        id_product = request.data.get('id_product')
        image = request.FILES.get('image')
        if not id_establisment or not id_product or not image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageField = image.read()

        ImageProduct.objects.create(id_establisment=Establisment.objects.get(id=id_establisment),
                                    id_product=Product.objects.get(id=id_product),
                                    image=imageField)
        return Response({'message': 'Image uploaded successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def getImageProduct(request):
    try:
        id_product = request.data.get('id_product')
        id_establisment = request.data.get('id_establisment')
        if not id_product or not id_establisment:   
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imagesList = []

        image = ImageProduct.objects.filter(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product))
        for image in image:
            imageBase64 = base64.b64encode(image.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url = f"data:{mime_type};base64,{imageBase64}"
            imagesList.append({"imagen": image_base64_url})
        
        return JsonResponse({'imagenes': imagesList})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
#@permission_classes([IsAuthenticated])
def updateImageProduct(request):
    
    try:
        id_establisment = request.data.get('id_establisment')
        id_product = request.data.get('id_product')
        id_image = request.data.get('id_image')
        image = request.FILES.get('image')
        if not id_establisment or not id_product or not id_image or not image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageField = image.read()

        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product), id=id_image)
        imageProduct.image = imageField
        imageProduct.save()
        return Response({'message': 'Image updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
#@permission_classes([IsAuthenticated])
def deleteImageProduct(request):
    try:
        id_establisment = request.data.get('id_establisment')
        id_product = request.data.get('id_product')
        id_image = request.data.get('id_image')
        if not id_establisment or not id_product or not id_image:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product), id=id_image)
        imageProduct.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)