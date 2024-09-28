from django.shortcuts import render
from rest_framework import viewsets
from .models import Color
from rest_framework.decorators import api_view
from establisment.models import Establisment
from django.http import JsonResponse
# Create your views here.
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
