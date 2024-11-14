import datetime

from rest_framework.response import Response
from rest_framework import status

from product.models import Product
from service.serializers import serviceSerializer
from .models import Establisment
import base64
import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from service.models import Service
from appointment.models import Appointment
from employee.models import Employee
from employee_services.models import EmployeeServices
from employee_services.serializers import employeeServicesSerializer
from rest_framework import status
from establisment.serializers import establismentSerializer
from employee.serializers import EmployeeSerializer
from employee_image.models import EmployeeImage
from review_employee.models import ReviewEmployee
from review_employee.serializers import reviewEmployeeSerializer
from image.models import Image
from review.models import Review
from review.serializers import reviewSerializer
from schedule.models import Time
from schedule.serializers import timeSerializer


# Create your views here.
@api_view(['POST'])
def createEstablisment(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        address = data.get('address')
        city = data.get('city')
        contact_methods = data.get('contact_methods')

        if not name or not address or not city or contact_methods is None:
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)

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
    
# Metodos para el apartado de finanzas
@api_view(['GET'])
def get_filter_payments_service(request, establisment_id):
    try:
        # Obtén el año y el mes de los parámetros de consulta
        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')
        services_list = [] 
        total_comission = 0
        ganancias_meses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_day = 0
        
        state = "Completada"
        
        # Verifica que los parámetros de año y mes están presentes
        if not year or not month:
            return JsonResponse({'error': 'Year, month and day are required parameters'}, status=400)
        
        # Busca el establecimiento
        establisment = Establisment.objects.get(id=establisment_id)
        # Filtra las citas por el establecimiento, estado, año y mes
        appointments = Appointment.objects.filter(
            establisment=establisment,
            estate__icontains=state,
            date__year=year
        )
        if not appointments.exists():
            return JsonResponse({'error': 'No appointments found'}, status=404) 
        
        for appointment in appointments:
            employee = Employee.objects.get(id=appointment.employee.id)
            appointment_services = []  
            total = 0
            pago_total = 0
            profit_employee = 0
            pago_total = 0
            
            for service in appointment.services.all():
                profit_establisment = service.price * service.commission
                profit_employee += service.price - profit_establisment
                total += profit_establisment
                pago_total += service.price
                appointment_services.append({
                    'service_name': service.name,
                    'service_price': service.price,
                    'commission_percentage': service.commission,
                    'profit_establisment': total})
                
            if appointment.date.day == int(day) and appointment.date.month == int(month) and appointment.date.year == int(year):
                total_day += total
                total_comission += profit_employee
                services_list.append({
                    'profit_establisment': total,
                    'appointment_id': appointment.id,
                    'client': appointment.client.user.first_name + ' ' + appointment.client.user.last_name,
                    'total': pago_total,
                    'date': appointment.date,
                    'employee': employee.user.first_name + ' ' + employee.user.last_name,
                    'time': appointment.time,
                    'services': appointment_services,
            })
            ganancias_meses[int(appointment.date.month)-1] += total
                      
        total_year = sum(ganancias_meses)
        
        return JsonResponse({
            'ganancias_meses': ganancias_meses[int(month)-1],
            'ganancias_año': total_year,
            'ganancia_establecimiento': total_day,
            'ganancia_employee': total_comission,
            'appointments_services': services_list
        }, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'No establisment found'}, status=404)
    except EmployeeServices.DoesNotExist:
        return JsonResponse({'error': 'Employee service not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': "Something went wrong"}, status=500)

@api_view(['GET'])
def servicesByEstablisment(request, establisment_id):
    try:
        # Verificar si el establecimiento existe
        establisment = Establisment.objects.get(id=establisment_id)

        # Obtener los servicios del establecimiento
        services = Service.objects.filter(establisment=establisment, state=True)

        # Serializar y devolver la respuesta
        serializer = serviceSerializer(services, many=True)
        return JsonResponse({
            'services': serializer.data
        }, status=200)

    except Establisment.DoesNotExist:
        return Response({"error": "Establishment not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e: 
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
@api_view(['GET'])
def getInfoEstablisment(request):
    try:
        information_establishment = {}
        image_establishment = {
            "image_logo": " ",
            "image_banner": " "
        }
        # Obtén el establecimiento 'Stylos'
        stylos = Establisment.objects.get(name='Stylos')
        stylosSerializer = establismentSerializer(stylos)

        services = Service.objects.filter(establisment=stylos)
        servicesSerializer = serviceSerializer(services, many=True)

        information_establishment['stylos_info'] = stylosSerializer.data
        information_establishment['services_info'] = servicesSerializer.data
        
        reviews = Review.objects.filter(establisment=stylos)
        if reviews.count() != 0:
            reviewsSerializer = reviewSerializer(reviews, many=True)
            rating = 0
            count = 1
            for review in reviewsSerializer.data:
                nota = review['rating']
                rating = int(nota)/ count
                count += 1
            information_establishment['rating'] = rating
            information_establishment['reviews'] = count - 1
        
       
        #obtener imagenes del establecimiento
        image_logo = Image.objects.filter(establisment=stylos, code = 1).first()
        if image_logo:
            imageBase64 = base64.b64encode(image_logo.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url_logo = f"data:{mime_type};base64,{imageBase64}"
            image_establishment['image_logo'] = image_base64_url_logo
        image_banner = Image.objects.filter(establisment=stylos, code = 2).first()
        if image_banner:
            imageBase64 = base64.b64encode(image_banner.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url = f"data:{mime_type};base64,{imageBase64}"
            image_establishment['image_banner'] = image_base64_url
            


        # Devolver la respuesta con los datos de estilista y empleados
        return Response({
            'information_establishment': information_establishment,
            'image_establishment': image_establishment
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getInfoEmployee(request):
    try:
        id = request.query_params.get('id_employee')
        employee = Employee.objects.get(id=id)
        employeeSerializer = EmployeeSerializer(employee)
        employe_data = {}
        data = employeeSerializer.data
        employe_data['id'] = data['id']
        employe_data['first_name'] = data['user']['first_name']
        employe_data['last_name'] = data['user']['last_name']
        employe_data['email'] = data['user']['email']
        employe_data['phone'] = data['phone']
        employe_data['state'] = data['state']
        employe_data['code'] = data['code']
        reviews = ReviewEmployee.objects.filter(employee=id)
        if reviews:
            data_review = reviewEmployeeSerializer(reviews, many=True).data
            rating = 0
            count = 1
            for review in data_review:
                nota = review['rating']
                rating = int(nota)/ count
                count += 1
            employe_data['rating'] = rating
            employe_data['reviews'] = count - 1
            image = EmployeeImage.objects.filter(establishment_id=employee.establisment.id, employee_id=employee.id).first()
        if image:
            imageBase64 = base64.b64encode(image.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url = f"data:{mime_type};base64,{imageBase64}"
            employe_data['image'] = image_base64_url
        time = Time.objects.filter(employee=id).first()
        if time:
            employe_data['time'] = timeSerializer(time).data
            del employe_data['time']['employee']
        services = EmployeeServices.objects.filter(employee=id)
        if services:
            employe_data['services'] = employeeServicesSerializer(services, many=True).data
            for service in employe_data['services']:
                del service['commission']
                del service['employee']
                del service['service']['establisment']
                del service['service']['commission'] 
        return Response(employe_data, status=status.HTTP_200_OK)
    except Exception as e:  
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getEmployees(request):
    try:
        establisment = Establisment.objects.get(name="Stylos")
        employees = Employee.objects.filter(establisment=establisment)
        data = EmployeeSerializer(employees, many=True).data
        for employee in data:
            del employee['establisment']
            del employee['user']['username']
            del employee['googleid']
            del employee['accestoken']
            del employee['token']
            services = EmployeeServices.objects.filter(employee=employee['id'])
            if services:
                employee['employee_services'] = employeeServicesSerializer(services, many=True).data
                for service in employee['employee_services']:
                    del service['commission']
                    del service['employee']
                    del service['service']['establisment']
                    del service['service']['commission']
            reviews = ReviewEmployee.objects.filter(employee=employee['id'])
            if reviews:
                data_review = reviewEmployeeSerializer(reviews, many=True).data
                rating = 0
                count = 1
                for review in data_review:
                    nota = review['rating']
                    rating = int(nota)/ count
                    count += 1
                employee['rating'] = rating
                employee['reviews'] = count - 1
            image = EmployeeImage.objects.filter(establishment_id=establisment.id, employee_id=employee['id']).first()
            if image:
                imageBase64 = base64.b64encode(image.image).decode('utf-8')
                mime_type = "image/jpeg"
                image_base64_url = f"data:{mime_type};base64,{imageBase64}"
                employee['image'] = image_base64_url
            time = Time.objects.filter(employee=employee['id']).first()
            if time:
                employee['time'] = timeSerializer(time).data
        return Response({'employeesList': data}, status=status.HTTP_200_OK)
    except Exception as e:  
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)