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
    image_file = request.FILES.get('image')

    if not image_file:
        return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)

    description = request.POST.get('description', '')
    code = 1

    Image.objects.create(
        establisment=establisment,
        image=image_file.read(),
        description=description,
        code=code,
        category=None,
        type=None,
    )

    return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)

@api_view(['GET'])
def get_logo(request, establisment_id):
    try:
        image_obj = Image.objects.filter(establisment=establisment_id, code=1).first()
        
        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        image_binaria = image_obj.image
        image_base64 = base64.b64encode(image_binaria).decode('utf-8')

        mime_type = "image/jpeg"
        image_base64_url = f"data:{mime_type};base64,{image_base64}"

        return JsonResponse({
            'imagen_base64': image_base64_url,
            'descripcion': image_obj.description,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PATCH'])
def update_logo(request, establisment_id):
    try:        
        image_obj = Image.objects.filter(establisment=establisment_id, code=1).first()
        if not image_obj:
            return JsonResponse({'error': 'Logo no encontrado'}, status=404)         
        new_image = request.FILES.get('image')
        if new_image:
            image_obj.image = new_image.read()
        image_obj.save()
        return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)
    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)
    except Exception as e:
        print(f"Error: {str(e)}")  
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
    image_file = request.FILES.get('image')

    if not image_file:
        return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)

    description = request.POST.get('description', '')
    code = 2

    Image.objects.create(
        establisment=establisment,
        image=image_file.read(),
        description=description,
        code=code,
        category=None,
            ype=None,
        )

    return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)

@api_view(['GET'])
def get_banner(request, establisment_id):
    try:
        image_obj = Image.objects.filter(establisment=establisment_id, code=2).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        image_binaria = image_obj.image
        image_base64 = base64.b64encode(image_binaria).decode('utf-8')

        mime_type = "image/jpeg" 
        image_base64_url = f"data:{mime_type};base64,{image_base64}"

        return JsonResponse({
            'image_base64': image_base64_url,
            'description': image_obj.descripcion,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['PATCH'])
def update_banner(request, establisment_id):
    try:           
        image_obj = Image.objects.filter(establisment=establisment_id, code=1).first()

        if not image_obj:
            return JsonResponse({'error': 'Logo no encontrado'}, status=404)

        new_image = request.FILES.get('image')

        if new_image:
            image_obj.image = new_image.read()
            
        image_obj.save()

        return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

    except Exception as e:
        print(f"Error: {str(e)}")
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