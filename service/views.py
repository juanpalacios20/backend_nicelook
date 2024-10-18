import base64
from django.http import JsonResponse
from django.shortcuts import render
from .models import Service
from .serializers import serviceSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from establisment.models import Establisment
from service.models import ImageService

# Create your views here.

class serviceViewSet(viewsets.ModelViewSet):
    serializer_class = serviceSerializer
    queryset = Service.objects.all()
    

#CREAR SERVICIO
@api_view(["POST"])
#@permission_classes([IsAuthenticated])
def create_service(request):
    #Se obtiene los parametros enviados por parte del front
    #data = request.data
    establishment_id = request.data.get("establishment_id")
    name = request.data.get("name")
    price = request.data.get("price")
    commission = request.data.get("commission")
    category = request.data.get("category")
    commission = int(commission)
    print('id', establishment_id)
    print('name', name)
    print('price', price)
    print('commission', commission)
    print('category', category)


    if commission < 0 or commission > 100:
        return Response(
            {"error": "La comisión debe ser un número entre 0 y 100."}, status=status.HTTP_400_BAD_REQUEST
        )
    commission = commission/100
        
    #Se crea un diccionario con los atributos necesarios para crear un objeto de tipo servicio
    service_data = {
        "name": name,
        "price": price,
        #"duration": data.get("duration"),
        "commission": commission,
        "category": category,
        "state": True
    }
    
    try:
        print("entro")
        try: 
            service = Service.objects.create(**service_data, establisment=Establisment.objects.get(id=establishment_id))
            print("creo")
            service.save()
            return Response(
                {
                    "message": "Servicio creado con éxito."
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(
                {"error": "No se pudo crear el servicio."}, status=status.HTTP_400_BAD_REQUEST
            )
            
    except:
        return Response(
            {"error": "No se pudo crear el servicio."}, status=status.HTTP_400_BAD_REQUEST
        )
    
    
#ACTUALIZAR SERVICIO
@api_view(["PUT"])
#@permission_classes([IsAuthenticated])
def update_service(request):
    id = request.data.get("service_id")
    print(id)
    try:
        service = Service.objects.get(id=id)
        print(service)
    
    except Service.DoesNotExist:
        #Si no existe un servicio con el id enviado se responde con un codigo 404
        return Response(
            {"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
        
    #Se obtiene los parametros enviados por parte del front
    service_data = request.data
    print(service_data)
    
    #Se actualiza el atributo correspondiente
    
    if "name" in service_data:
        service.name = service_data["name"]
    
    if "price" in service_data:
        service.price = service_data["price"]
    
    #if "duration" in service_data:
        #service.duration = service_data["duration"]
        
    if "commission" in service_data:
        service.commission = int(service_data["commission"]) / 100
    
    if "category" in service_data:
        service.category = service_data["category"]
    
    if "state" in service_data:
        service.state = service_data["state"]
        
     # Guardar la nueva informacion 
    service.save()

    # Serializar y devolver el servicio actualizado
    serializer = serviceSerializer(service)
    return Response(
        {
            "message": "Informacion del servicio actualizada con éxito.",
            "service": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

#ELIMINAR SERVICIO
@api_view(["DELETE"])
#@permission_classes([IsAuthenticated])
def delete_service(request):
    id = request.data.get("idService")
    print("id", id)
    try:
        #Se obtiene el id del servicio y se busca en la base de datos
        print("entrando al try")
        service = Service.objects.get(id=id)
        print("saliendo")
        print('service', service)
        
    except Service.DoesNotExist:
        #Si no existe un servicio con el id enviado se responde con un codigo 404
        return Response(
            {"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
    
    #Se elimina el servicio de la base de datos
    print("eliminando")
    service.delete()
    print("eliminado")
    
    #Se envia un mensaje de satisfaccion del la accion
    return Response(
        {
            "message": "Servicio eliminado con exito.",
        },
        status=status.HTTP_200_OK,
    )

#ENLISTAR SERVICIO
@api_view(["GET"])
#@permission_classes([IsAuthenticated])
def list_service(request):
    services = None
    establisment_id = request.query_params.get("establishment_id")
    print('id', establisment_id)
    try:
        #Se obtienen todos los servicios que se encuentran en la base de datos
        services = Service.objects.filter(establisment = establisment_id)
        
    except services is None:
        #Si la lista es vacia, se devulve un mensaje informando que no hay servicios registrados
        return Response(
            {"message": "Actualmente no hay servicios registrados"}, status=status.HTTP_404_NOT_FOUND
        )

    #Se crea un diccionario donde se mostrara la informacion de cada servicio
    serializer = serviceSerializer(services, many=True)

    #Se envia la informacion y un codigo http 200
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
#@permission_classes([IsAuthenticated])  # Descomentar si necesitas autenticación
def filter_by_category(request):
    category = request.query_params.get("category")
    if not category:
        return Response( 
            {"error": "No se ha especificado una categoría."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try: 
        services = Service.objects.filter(category=category)
        
        if not services.exists():
            return Response(
                {"error": "No se encontraron servicios en la categoría especificada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = serviceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Service.DoesNotExist:
        return Response(
            {"error": "No se encontraron servicios en la categoría especificada."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Error en el servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(["POST"])
def upload_photo_service(request, service_id, establisment_id):
    try:
        image_file = request.FILES["image"]
        establisment = Establisment.objects.get(id=establisment_id)
        service = Service.objects.get(id=service_id)
        
        if not establisment:
            return JsonResponse({'error': 'The establishment has not been provided'}, status=400)
        if not service:
            return JsonResponse({'error': 'The service has not been provided'}, status=400)
        
        if not image_file:
            return JsonResponse({'error': 'The image has not been provided'}, status=400)
        imageService = ImageService.objects.filter(establisment=establisment, service=service).first()
        
        if imageService:
            imageService.image = image_file.read()
            imageService.save()
            return JsonResponse({'success': 'The image has been updated successfully'}, status=200)
        
        image_data = image_file.read()
        image = ImageService.objects.create(
            establisment=establisment,
            service=service,
            image=image_data
        )
        image.save()
        return JsonResponse(
            {'success': 'The image has been uploaded successfully'}, status=400
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
      
@api_view(["GET"])
def get_photo_service(request, service_id, establisment_id):
    try:
        #filtra el logo del establecimiento
        image_obj = ImageService.objects.filter(establisment=establisment_id, service=service_id ).first()

        if not image_obj:
            return JsonResponse({'error': 'Image not found'}, status=404)

        #convierte la imagen binaria a base64
        image_binaria = image_obj.image
        image_base64 = base64.b64encode(image_binaria).decode('utf-8')

        #convierte la imagen base64 a url
        mime_type = "image/jpeg"
        image_base64_url = f"data:{mime_type};base64,{image_base64}"

        return JsonResponse({
            'imagen_base64': image_base64_url,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
@api_view(["DELETE"])
def delete_photo_service(request, service_id, establisment_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        image_obj = ImageService.objects.filter(establisment=establisment, service=service_id).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

        image_obj.delete()

        return JsonResponse({'mensaje': 'Imagen eliminada exitosamente'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)