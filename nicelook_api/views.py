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
def subir_logo(request, establecimiento_id):
    if request.method == 'POST':
        establecimiento = Establisment.objects.get(id=establecimiento_id)
        imagen_archivo = request.FILES.get('imagen')

        if not imagen_archivo:
            return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)

        descripcion = request.POST.get('descripcion', '')
        codigo = 1

        Image.objects.create(
            establecimiento=establecimiento,
            imagen=imagen_archivo.read(),
            descripcion=descripcion,
            codigo=codigo,
            categoria=NULL,
            tipo=NULL,
        )

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_logo(request, establecimiento_id):
    try:

        imagen_obj = Image.objects.filter(establecimiento=establecimiento_id, codigo=1).first()

        if not imagen_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        imagen_binaria = imagen_obj.imagen
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')

        mime_type = "image/jpeg"
        imagen_base64_url = f"data:{mime_type};base64,{imagen_base64}"

        return JsonResponse({
            'imagen_base64': imagen_base64_url,
            'descripcion': imagen_obj.descripcion,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def actualizar_logo(request, establecimiento_id):
    if request.method == 'PUT':
        try:
            # Obtener el primer objeto del QuerySet para el logo que deseas actualizar
            imagen_obj = Image.objects.filter(establecimiento=establecimiento_id, codigo=1).first()

            if not imagen_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Obtener los datos enviados en la solicitud
            nueva_imagen = request.FILES.get('imagen')

            if nueva_imagen:
                # Actualizar la imagen
                imagen_obj.imagen = nueva_imagen.read()

            # Guardar los cambios
            imagen_obj.save()

            return JsonResponse({'mensaje': 'Logo actualizado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            print(f"Error: {str(e)}")  # Debug: imprime el error en la consola
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
def borrar_logo(request, establecimiento_id):
    if request.method == 'DELETE':
        try:
            # Buscar el establecimiento y el logo
            establecimiento = Establisment.objects.get(id=establecimiento_id)
            imagen_obj = Image.objects.filter(establecimiento=establecimiento, codigo=1).first()

            if not imagen_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Eliminar el logo
            imagen_obj.delete()

            return JsonResponse({'mensaje': 'Logo eliminado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def subir_banner(request, establecimiento_id):
    if request.method == 'POST':
        establecimiento = Establisment.objects.get(id=establecimiento_id)
        imagen_archivo = request.FILES.get('imagen')

        if not imagen_archivo:
            return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)

        descripcion = request.POST.get('descripcion', '')
        codigo = 2

        Image.objects.create(
            establecimiento=establecimiento,
            imagen=imagen_archivo.read(),
            descripcion=descripcion,
            codigo=codigo,
            categoria=NULL,
            tipo=NULL,
        )

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_banner(request, establecimiento_id):
    try:
        imagen_obj = Image.objects.filter(establecimiento=establecimiento_id, codigo=2).first()

        if not imagen_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        imagen_binaria = imagen_obj.imagen
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')

        mime_type = "image/jpeg" 
        imagen_base64_url = f"data:{mime_type};base64,{imagen_base64}"

        return JsonResponse({
            'imagen_base64': imagen_base64_url,
            'descripcion': imagen_obj.descripcion,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def borrar_banner(request, establecimiento_id):
    if request.method == 'DELETE':
        try:
            # Buscar el establecimiento y el logo
            establecimiento = Establisment.objects.get(id=establecimiento_id)
            imagen_obj = Image.objects.filter(establecimiento=establecimiento, codigo=2).first()

            if not imagen_obj:
                return JsonResponse({'error': 'Logo no encontrado'}, status=404)

            # Eliminar el logo
            imagen_obj.delete()

            return JsonResponse({'mensaje': 'Logo eliminado exitosamente'}, status=200)

        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def guardar_color(request, establecimiento_id):
    if request.method == 'POST':
        try:
            establecimiento = Establisment.objects.get(id=establecimiento_id)
        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        codigo_color = request.POST.get('codigo_color')
        if not codigo_color:
            return JsonResponse({'error': 'No se ha proporcionado ningún código para el color de establecimiento'}, status=400)

        try:
            Color.objects.create(
                establecimiento=establecimiento,
                codigo=codigo_color
            )
        except Exception as e:
            return JsonResponse({'error': f'Error al guardar el color: {str(e)}'}, status=500)

        return JsonResponse({'mensaje': 'Color guardado exitosamente'}, status=201)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_color(request, color_id):
    if request.method == 'GET':
        try:
            
            color = Color.objects.get(id=color_id)
            codigo_color = color.codigo
            
            establecimiento = color.establecimiento

            return JsonResponse({
                'color': codigo_color,
                'establecimiento': {
                    'id': establecimiento.id,
                    'nombre': establecimiento.nombre  
                }
            })
        except Color.DoesNotExist:
            return JsonResponse({'error': 'Código de color no encontrado'}, status=404)
        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def crearEstablecimiento(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de la solicitud
            data = json.loads(request.body)
            nombre = data.get('nombre')
            direccion = data.get('direccion')
            ciudad = data.get('ciudad')
            metodos_contacto = data.get('metodos_contacto')
            servicios_ids = data.get('servicios')

            if not nombre or not direccion or not ciudad or not metodos_contacto or not servicios_ids:
                return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)

            establecimiento = Establisment.objects.create(
                nombre=nombre,
                direccion=direccion,
                ciudad=ciudad,
                metodos_contacto=metodos_contacto
            )

            # Los ids al ser una relación con servicio, se agregan a parte
            servicios = Service.objects.filter(id__in=servicios_ids)
            if servicios.exists():
                establecimiento.servicios.set(servicios)
            else:
                return JsonResponse({'error': 'Los servicios no son válidos'}, status=400)

            # esto nomas es para visualizar que todo esté agregado correctamente
            return JsonResponse({
                'mensaje': 'Establecimiento creado exitosamente',
                'establecimiento': {
                    'id': establecimiento.id,
                    'nombre': establecimiento.nombre,
                    'direccion': establecimiento.direccion,
                    'ciudad': establecimiento.ciudad,
                    'metodos_contacto': establecimiento.metodos_contacto,
                    'servicios': list(servicios.values('id', 'nombre', 'precio'))
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def cambiar_nombre(request, establecimiento_id):
    if request.method == 'POST':
        establecimiento = Establisment.objects.get(id=establecimiento_id)
        nombre = request.data.get('nombre')

        if not nombre:
            return JsonResponse({'error': 'No se ha proporcionado ningun nombre'}, status=400)

        establecimiento.nombre = nombre
        establecimiento.save()

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def cambiar_direccion(request, establecimiento_id):
    if request.method == 'POST':
        establecimiento = Establisment.objects.get(id=establecimiento_id)
        direccion = request.data.get('direccion')

        if not direccion:
            return JsonResponse({'error': 'No se ha proporcionado ningun nombre'}, status=400)

        establecimiento.direccion = direccion
        establecimiento.save()

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)



        
        
    


