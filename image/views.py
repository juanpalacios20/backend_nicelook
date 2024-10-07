from django.shortcuts import render
from rest_framework import viewsets
from .models import Image
from .serializers import imageSerializer
import base64
import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from establisment.models import Establisment

# Create your views here.
@api_view(['POST'])
def upload_logo(request, establisment_id):
    
    establisment = Establisment.objects.get(id=establisment_id)
    image = Image.objects.filter(establisment=establisment, code=1).first()
    #image es el campo que contiene la imagen que quieres subir para el logo
    if image:   
            new_image = request.data.get('image')
            image_bytes = new_image.encode('utf-8')
            if new_image:
               image.image = image_bytes
            image.save()
            return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)   
        
    image_file = request.data.get('image')
    image_bytes = image_file.encode('utf-8')
    if not image_file:
        return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)
    #según mi planteamiento, 1 es para el logo y 2 es para el banner
    code = 1

    Image.objects.create(
        establisment=establisment,
        image=image_bytes,
        description="logo",
        code=code,
        #segun mi planteamiento, en logo y banner no hay categoría ni tipo
        category=None,
        type=None,
    )
    
    return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)

@api_view(['GET'])
def get_logo(request, establisment_id):
    try:
        # filtra el logo del establecimiento
        image_obj = Image.objects.filter(establisment=establisment_id, code=1).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        # convierte el binario a string
        image_binary = image_obj.image.tobytes()
        image_string = image_binary.decode('utf-8')

        return JsonResponse({
            'imagen': image_string,
            'descripcion': image_obj.description,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_logo(request, establisment_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        image_obj = Image.objects.filter(establisment=establisment, code=1).first()

        if not image_obj:
            return JsonResponse({'error': 'Logo no encontrado'}, status=404)


        image_obj.delete()

        return JsonResponse({'mensaje': 'Logo eliminado exitosamente'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
@api_view(['POST'])
def upload_banner(request, establisment_id):
        
    establisment = Establisment.objects.get(id=establisment_id)
    image = Image.objects.filter(establisment=establisment, code=2).first()
    #image es el campo que contiene la imagen que quieres subir para el logo
    if image:   
            new_image = request.data.get('image')
            image_bytes = new_image.encode('utf-8')
            if new_image:
               image.image = image_bytes
            image.save()
            return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)   
        
    image_file = request.data.get('image')
    image_bytes = image_file.encode('utf-8')
    if not image_file:
        return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)
    #según mi planteamiento, 1 es para el logo y 2 es para el banner
    code = 1

    Image.objects.create(
        establisment=establisment,
        image=image_bytes,
        description="banner",
        code=code,
        #segun mi planteamiento, en logo y banner no hay categoría ni tipo
        category=None,
        type=None,
    )
    
    return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)

@api_view(['GET'])
def get_banner(request, establisment_id):
    try:
        # filtra el logo del establecimiento
        image_obj = Image.objects.filter(establisment=establisment_id, code=2).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        # convierte el binario a string
        image_binary = image_obj.image.tobytes()
        image_string = image_binary.decode('utf-8')

        return JsonResponse({
            'imagen': image_string,
            'descripcion': image_obj.description,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_banner(request, establisment_id):
        try:
            # Buscar el establecimiento y el logo
            establisment = Establisment.objects.get(id=establisment_id)
            image_obj = Image.objects.filter(establisment=establisment, code=2).first()

            if not image_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Eliminar el logo
            image_obj.delete()

            return JsonResponse({'mensaje': 'Logo eliminado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500) 