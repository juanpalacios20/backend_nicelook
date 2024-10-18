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