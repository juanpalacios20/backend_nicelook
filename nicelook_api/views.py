from django.http import JsonResponse
from imagenes.models import ImagenEstablecimiento
from establecimiento.models import Establecimiento
from colores.models import Colores
from django.views.decorators.csrf import csrf_exempt
import base64

@csrf_exempt
def subir_imagen(request, establecimiento_id):
    if request.method == 'POST':
        establecimiento = Establecimiento.objects.get(id=establecimiento_id)
        imagen_archivo = request.FILES.get('imagen')

        if not imagen_archivo:
            return JsonResponse({'error': 'No se ha proporcionado ninguna imagen'}, status=400)

        descripcion = request.POST.get('descripcion', '')

        # Guardar la imagen como binario en la base de datos
        ImagenEstablecimiento.objects.create(
            establecimiento=establecimiento,
            imagen=imagen_archivo.read(),  # Convierte la imagen en binario
            descripcion=descripcion
        )

        return JsonResponse({'mensaje': 'Imagen subida exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_imagen(request, imagen_id):
    try:
        imagen_obj = ImagenEstablecimiento.objects.get(id=imagen_id)
        imagen_binaria = imagen_obj.imagen
        
        # Convertir a base64
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')
        
        # Construir la URL de la imagen en base64
        mime_type = "image/jpeg"  # Dependiendo del formato de imagen que estés almacenando
        imagen_base64_url = f"data:{mime_type};base64,{imagen_base64}"

        return JsonResponse({
            'imagen_base64': imagen_base64_url,
            'descripcion': imagen_obj.descripcion,
        })
    except ImagenEstablecimiento.DoesNotExist:
        return JsonResponse({'error': 'Imagen no encontrada'}, status=404)
    
@csrf_exempt
def guardar_color(request, establecimiento_id):
    if request.method == 'POST':
        try:
            establecimiento = Establecimiento.objects.get(id=establecimiento_id)
        except Establecimiento.DoesNotExist:
            return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

        codigo_color = request.POST.get('codigo_color')
        if not codigo_color:
            return JsonResponse({'error': 'No se ha proporcionado ningún código para el color de establecimiento'}, status=400)

        try:
            Colores.objects.create(
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
            # Obtener el color
            color = Colores.objects.get(id=color_id)
            codigo_color = color.codigo
            
            # Obtener el establecimiento relacionado
            establecimiento = color.establecimiento  # Esto ahora es un solo objeto Establecimiento

            return JsonResponse({
                'color': codigo_color,
                'establecimiento': {
                    'id': establecimiento.id,
                    'nombre': establecimiento.nombre  # Asegúrate de que el campo 'nombre' exista en tu modelo
                }
            })
        except Colores.DoesNotExist:
            return JsonResponse({'error': 'Código de color no encontrado'}, status=404)
        except Exception as e:  # Captura cualquier otro error
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


        
        
    


