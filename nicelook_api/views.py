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

@csrf_exempt
def upload_logo(request, establisment_id):
    if request.method == 'POST':
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
    return JsonResponse({'error': 'Método no permitido'}, status=405)

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
    
@csrf_exempt
def update_logo(request, establisment_id):
    if request.method == 'PUT':
        try:
            # Obtener el primer objeto del QuerySet para el logo que deseas actualizar
            image_obj = Image.objects.filter(establisment=establisment_id, code=1).first()

            if not image_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Obtener los datos enviados en la solicitud
            new_image = request.FILES.get('image')

            if new_image:
                # Actualizar la imagen
                image_obj.image = new_image.read()

            # Guardar los cambios
            image_obj.save()

            return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            print(f"Error: {str(e)}")  # Debug: imprime el error en la consola
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
def delete_logo(request, establisment_id):
    if request.method == 'DELETE':
        try:
            # Buscar el establecimiento y el logo
            establisment = Establisment.objects.get(id=establisment_id)
            image_obj = Image.objects.filter(establisment=establisment, code=1).first()

            if not image_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Eliminar el logo
            image_obj.delete()

            return JsonResponse({'mensaje': 'Logo eliminado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def upload_banner(request, establisment_id):
    if request.method == 'POST':
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
            type=None,
        )

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
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

@csrf_exempt
def delete_banner(request, establisment_id):
    if request.method == 'DELETE':
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

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def upload_color(request, establisment_id):
    if request.method == 'POST':
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

    return JsonResponse({'error': 'Método no permitido'}, status=405)

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

@csrf_exempt
def createEstablisment(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de la solicitud
            data = json.loads(request.body)
            name = data.get('name')
            address = data.get('address')
            city = data.get('city')
            contact_methods = data.get('contact_methods')
            services_ids = data.get('services')

            if not name or not address or not city or not contact_methods or not services_ids:
                return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)

            establisment = Establisment.objects.create(
                name=name,
                direccion=address,
                ciudad=city,
                contact_methods=contact_methods
            )

            # Los ids al ser una relación con servicio, se agregan a parte
            services = Service.objects.filter(id__in=services_ids)
            if services.exists():
                establisment.services.set(services)
            else:
                return JsonResponse({'error': 'Los servicios no son válidos'}, status=400)

            # esto nomas es para visualizar que todo esté agregado correctamente
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

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def change_name(request, establisment_id):
    if request.method == 'POST':
        establisment = Establisment.objects.get(id=establisment_id)
        name = request.data.get('name')

        if not name:
            return JsonResponse({'error': 'No se ha proporcionado ningun nombre'}, status=400)

        establisment.name = name
        establisment.save()

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def change_adress(request, establisment_id):
    if request.method == 'POST':
        establisment = Establisment.objects.get(id=establisment_id)
        address = request.data.get('address')

        if not address:
            return JsonResponse({'error': 'No se ha proporcionado ningun nombre'}, status=400)

        establisment.address = address
        establisment.save()

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)



        
        
    


