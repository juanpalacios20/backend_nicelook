from django.shortcuts import render
from .models import Service
from .serializers import serviceSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class serviceViewSet(viewsets.ModelViewSet):
    serializer_class = serviceSerializer
    queryset = Service.objects.all()
    

#CREAR SERVICIO
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_service(request):
    #Se obtiene los parametros enviados por parte del front
    data = request.data
    
    #Se crea un diccionario con los atributos necesarios para crear un objeto de tipo servicio
    service_data = {
        "name": data.get("name"),
        "price": data.get("price"),
        #"duration": data.get("duration"),
        "commission": data.get("commission"),
        "category": data.get("category"),
    }
    
    #Se le pasa el diccionario al serializador para crear el objeto
    serializer = serviceSerializer(data=service_data)
    if serializer.is_valid():
        try:
            service = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#ACTUALIZAR SERVICIO
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_service(request):
    
    try:
        #Se obtiene el id del servicio y se busca en la base de datos
        service = Service.objects.get(id= request.query_params.get("service_id"))
    
    except service.DoesNotExist:
        #Si no existe un servicio con el id enviado se responde con un codigo 404
        return Response(
            {"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
        
    #Se obtiene los parametros enviados por parte del front
    service_data= request.data
    
    #Se actualiza el atributo correspondiente
    
    if "name" in service_data:
        service.name = service_data["name"]
    
    if "price" in service_data:
        service.price = service_data["price"]
    
    #if "duration" in service_data:
        #service.duration = service_data["duration"]
        
    if "commission" in service_data:
        service.commission = service_data["commission"]
    
    if "category" in service_data:
        service.category = service_data["category"]
        
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
@permission_classes([IsAuthenticated])
def delete_service(request):
    
    try:
        #Se obtiene el id del servicio y se busca en la base de datos
        service = Service.objects.get(id= request.query_params.get("service_id"))
        
    except service.DoesNotExist:
        #Si no existe un servicio con el id enviado se responde con un codigo 404
        return Response(
            {"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
    
    #Se elimina el servicio de la base de datos
    service.delete()
    
    #Se envia un mensaje de satisfaccion del la accion
    return Response(
        {
            "message": "Servicio eliminado con exito.",
        },
        status=status.HTTP_200_OK,
    )

#ENLISTAR SERVICIO
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_service(request):
    
    try:
        #Se obtienen todos los servicios que se encuentran en la base de datos
        services= serviceSerializer.objects.all()
        
    except services is None:
        #Si la lista es vacia, se devulve un mensaje informando que no hay servicios registrados
        return Response(
            {"message": "Actualmente no hay servicios registrados"}, status=status.HTTP_404_NOT_FOUND
        )

    #Se crea un diccionario donde se mostrara la informacion de cada servicio
    service_data=[
        {
            "Name": service.name,
            "Price": service.price,
            "Duration": service.duration,
            "Commission": service.commission,
            "Category": service.category
        }
        for service in services
    ]

    #Se envia la informacion y un codigo http 200
    return Response(service_data, status=status.HTTP_200_OK)