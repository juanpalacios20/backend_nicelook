#aqui va toda la magia, bienvenidos a disneyland
from asyncio.windows_events import NULL
from django.http import JsonResponse
from image.models import Image
from establisment.models import Establisment
from color.models import Color
from service.models import Service
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from rest_framework.decorators import api_view

@api_view(['POST'])
@csrf_exempt
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
        category=NULL,
        type=NULL,
    )

    return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)

@api_view(['GET'])
@csrf_exempt
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
@csrf_exempt
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
@csrf_exempt
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
@csrf_exempt
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

@api_view(['PATCH'])
def upload_color(request, establisment_id):
        try:
            establisment = Establisment.objects.get(id=establisment_id)
        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        code_color = request.POST.get('code_color')
        if not code_color:
            return JsonResponse({'error': 'No se ha proporcionado ningún código para el color de establecimiento'}, status=400)

        try:
            Color.objects.create(
                establisment=establisment,
                code=code_color
            )
        except Exception as e:
            return JsonResponse({'error': f'Error al guardar el color: {str(e)}'}, status=500)

        return JsonResponse({'mensaje': 'Color guardado exitosamente'}, status=201)

@api_view(['GET'])
def get_color(request, color_id):
    if request.method == 'GET':
        try:
            
            color = Color.objects.get(id=color_id)
            code_color = color.code
            
            establisment = color.establisment

            return JsonResponse({
                'color': code_color,
                'establecimiento': {
                    'id': establisment.id,
                    'nombre': establisment.name  
                }
            })
        except Color.DoesNotExist:
            return JsonResponse({'error': 'Código de color no encontrado'}, status=404)
        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['POST'])
def createEstablisment(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        address = data.get('address')
        city = data.get('city')
        contact_methods = data.get('contact_methods')  # Se espera que sea un diccionario JSON
        services_ids = data.get('services')

        if not name or not address or not city or contact_methods is None or not services_ids:
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)

        establisment = Establisment.objects.create(
            name=name,
            direccion=address,
            ciudad=city,
            contact_methods=contact_methods
        )
        services = Service.objects.filter(id__in=services_ids)
        if services.exists():
            establisment.services.set(services)
        else:
            return JsonResponse({'error': 'Los servicios no son válidos'}, status=400)

        return JsonResponse({
            'mensaje': 'Establecimiento creado exitosamente',
            'establecimiento': {
                'id': establisment.id,
                'name': establisment.name,
                'address': establisment.address,
                'city': establisment.city,
                'contact_methods': establisment.contact_methods,
                'services': list(services.values('id', 'name', 'price'))
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

        
@api_view(['PATCH'])
def update_establisment(request, establisment_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)

        # Obtener los datos del request y verificar si fueron enviados
        name = request.data.get('name')
        address = request.data.get('address')
        city = request.data.get('city')
        contact_methods = request.data.get('contact_methods')  # Agregar esta línea

        # Actualizar los campos solo si los valores fueron proporcionados
        if name:
            establisment.name = name
        if address:
            establisment.address = address
        if city:
            establisment.city = city
        if contact_methods is not None:  # Solo actualizar si se proporciona un valor
            establisment.contact_methods = contact_methods

        # Guardar los cambios en la base de datos
        establisment.save()

        return JsonResponse({'mensaje': 'Establecimiento actualizado correctamente'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
@api_view(['GET'])
def get_establisment(request, establisment_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)

        return JsonResponse({
            'id': establisment.id,
            'name': establisment.name,
            'address': establisment.address,
            'city': establisment.city,
            'contact_methods': establisment.contact_methods,  
            'services': list(establisment.services.values('id', 'name', 'price'))  
        }, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no existe'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




        
        
    


