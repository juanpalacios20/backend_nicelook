from .models import Establisment
import base64
import json
from rest_framework.decorators import api_view
from django.http import JsonResponse

# Create your views here.
@api_view(['POST'])
def createEstablisment(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        address = data.get('address')
        city = data.get('city')
        contact_methods = data.get('contact_methods')

        establisment = Establisment.objects.create(
            name=name,
            direccion=address,
            ciudad=city,
            contact_methods=contact_methods
        )

        return JsonResponse({
            'mensaje': 'Establecimiento creado exitosamente',
            'establecimiento': {
                'id': establisment.id,
                'name': establisment.name,
                'address': establisment.address,
                'city': establisment.city,
                'contact_methods': establisment.contact_methods,
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
            'contact_methods': establisment.contact_methods
        }, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no existe'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


