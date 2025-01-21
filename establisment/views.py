from datetime import datetime, timedelta


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
from schedule.models import TimeException
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
def servicesByEstablisment(request, employee_id):
    try:
        # Verificar si el empleado existe
        employee = Employee.objects.get(id=employee_id)
        # Obtener los servicios del empleado
        employee_services = EmployeeServices.objects.filter(employee=employee)
        
        # Excluir los servicios del empleado y los servicios con estado en false
        services = Service.objects.exclude(id__in=[service.service.id for service in employee_services]).filter(state=True)
        
        # Serializar y devolver la respuesta
        serializer = serviceSerializer(services, many=True)
        return JsonResponse({
            'services': serializer.data
        }, status=200)

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
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
        stylos = Establisment.objects.get(name="Stylo's Peluquería & Barbería")
        stylosSerializer = establismentSerializer(stylos)

        services = Service.objects.filter(establisment=stylos)
        servicesSerializer = serviceSerializer(services, many=True)

        information_establishment['stylos_info'] = stylosSerializer.data
        information_establishment['services_info'] = servicesSerializer.data
        
        reviews = Review.objects.filter(establisment=stylos)
        if reviews.count() != 0:
            reviewsSerializer = reviewSerializer(reviews, many=True)
            rating = 0
            count = 0
            for review in reviewsSerializer.data:
                nota = review['rating']
                rating += int(nota)
                count += 1
            rating = round(rating / count, 2)
            information_establishment['rating'] = rating
            information_establishment['reviews'] = count
        
       
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
def getAvailableEmployees(request, id_employee):
    try:
        # Obtener parámetros de la consulta
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))
        day = int(request.query_params.get('day'))
        new_date = datetime(year=year, month=month, day=day)

        # Obtener empleado, horario y citas
        employee = Employee.objects.get(id=id_employee)
        time_ranges = Time.objects.filter(employee=employee)
        exception_ranges = TimeException.objects.filter(employee=employee)
        appointments = Appointment.objects.filter(
            date=new_date,
            employee=employee,
            estate__icontains='Pendiente'
        ).order_by('time')
        
        disponibilidad = []
        excepciones = []

        if not time_ranges:
            return Response({"error": "No se encontraron horarios para el empleado"}, status=status.HTTP_400_BAD_REQUEST)

        # Calcular disponibilidad para cada rango de tiempo
        for time_range in time_ranges:
            start_time = time_range.time_start_day_one
            end_time = time_range.time_end_day_one

            if time_range.double_day:
                start_time_two = time_range.time_start_day_two
                end_time_two = time_range.time_end_day_two

            if time_range.date_start > new_date.date() or time_range.date_end < new_date.date():
                continue  # Saltar horarios que no aplican para este día

            # Filtrar excepciones solo para el día actual
            current_exceptions = exception_ranges.filter(
                date_start__lte=new_date.date(),
                date_end__gte=new_date.date()
            )
            
            for exception in current_exceptions:
                excepciones.append({
                    'time_start': str(exception.time_start),
                    'time_end': str(exception.time_end)
                })

            # Verificar disponibilidad en el primer turno
            current_start_time = start_time
            for exception in current_exceptions:
                if exception.time_start and exception.time_end:
                    # Si hay un intervalo antes de la excepción
                    if current_start_time < exception.time_start:
                        disponibilidad.append((current_start_time, exception.time_start))
                    # Ajustar el inicio después de la excepción
                    if exception.time_end > current_start_time:
                        current_start_time = exception.time_end

            # Si queda tiempo después de la última excepción
            if current_start_time < end_time:
                disponibilidad.append((current_start_time, end_time))

            # Verificar disponibilidad en el segundo turno
            if time_range.double_day:
                current_start_time_two = start_time_two
                for exception in current_exceptions:
                    if exception.time_start and exception.time_end:
                        # Si hay un intervalo antes de la excepción
                        if current_start_time_two < exception.time_start:
                            disponibilidad.append((current_start_time_two, exception.time_start))
                        # Ajustar el inicio después de la excepción
                        if exception.time_end > current_start_time_two:
                            current_start_time_two = exception.time_end

                # Si queda tiempo después de la última excepción
                if current_start_time_two < end_time_two:
                    disponibilidad.append((current_start_time_two, end_time_two))

        # Formatear la respuesta con los intervalos de disponibilidad
        formatted_disponibilidad = [
            [str(time[0]), str(time[1])] for time in disponibilidad
        ]
        
        return Response({
            'disponibilidad': formatted_disponibilidad,
            'excepciones': excepciones
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

        # Inicializar `image` para evitar el error
        image = None

        # Obtener reseñas
        reviews = ReviewEmployee.objects.filter(employee=id)
        if reviews:
            data_review = reviewEmployeeSerializer(reviews, many=True).data
            rating = 0
            count = 0
            for review in data_review:
                nota = review['rating']
                rating += int(nota)
                count += 1
            # Calcular el promedio de calificaciones
            promedio = rating / count
            employe_data['rating'] = round(promedio, 1)
            print(employe_data['rating'])
            employe_data['reviews'] = count

            # Obtener la imagen del empleado
        image = EmployeeImage.objects.filter(employee_id=id).first()
        print(image)
        # Convertir la imagen a base64 si existe
        if image is not None:
            imageBase64 = base64.b64encode(image.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url = f"data:{mime_type};base64,{imageBase64}"
            employe_data['image'] = image_base64_url

        # Obtener el horario del empleado
        
        time = Time.objects.filter(employee=employee).first()
        if time:
            employe_data['time'] = timeSerializer(time).data
            del employe_data['time']['employee']

        # Obtener los servicios del empleado
        services = EmployeeServices.objects.filter(employee=id)
        if services:
            employe_data['services'] = employeeServicesSerializer(services, many=True).data
            for service in employe_data['services']:
                del service['employee']
                del service['service']['establisment']
                del service['service']['commission']
                
        return Response(employe_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['GET'])
def getEmployees(request):
    try:
        establisment = Establisment.objects.get(name="Stylo's Peluquería & Barbería")
        employees = Employee.objects.filter(establisment=establisment, state=True)
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
                    del service['duration']
                    del service['employee']
                    del service['service']['establisment']
                    del service['service']['commission']
            reviews = ReviewEmployee.objects.filter(employee=employee['id'])
            if reviews:
                data_review = reviewEmployeeSerializer(reviews, many=True).data
                rating = 0
                count = 0
                for review in data_review:
                    nota = review['rating']
                    rating += int(nota)
                    count += 1
                promedio = rating / count
                employee['rating'] = round(promedio, 1)
                employee['reviews'] = count
                print(employee['rating'])
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

def calcular_disponibilidad_por_turno(employee, date, appointments):
    """
    Calcula la disponibilidad completa de un empleado en una fecha específica,
    considerando los turnos, excepciones y citas programadas.
    
    :param employee: Empleado para el que se calcula la disponibilidad.
    :param date: Fecha para la cual calcular la disponibilidad.
    :param appointments: Lista de citas filtradas previamente.
    :return: Lista de intervalos de disponibilidad o mensaje indicando estado.
    """
    disponibilidad_completa = []

    # Filtrar turnos válidos para la fecha
    turnos = Time.objects.filter(
        employee=employee, date_start__lte=date, date_end__gte=date
    )

    if not turnos:
        return "El Artista aún no ha definido un horario para esta fecha."

    for turno in turnos:
        # Procesar primer turno del día
        turno_start_time = datetime.combine(date, turno.time_start_day_one)
        turno_end_time = datetime.combine(date, turno.time_end_day_one)

        # Si el turno es doble, procesar también el segundo turno
        if turno.double_day and turno.time_start_day_two and turno.time_end_day_two:
            turno_start_time_2 = datetime.combine(date, turno.time_start_day_two)
            turno_end_time_2 = datetime.combine(date, turno.time_end_day_two)

        # Filtrar excepciones para la fecha
        excepciones = TimeException.objects.filter(
            employee=employee, date_start__lte=date, date_end__gte=date
        )

        # Lista para los intervalos de disponibilidad
        disponibilidad_turno = []

        # Procesar cada turno (puede ser uno o dos por día)
        for start_time, end_time in [(turno_start_time, turno_end_time)] + (
            [(turno_start_time_2, turno_end_time_2)] if turno.double_day else []
        ):
            for excepcion in excepciones:
                if excepcion.time_start and excepcion.time_end:
                    excepcion_start = datetime.combine(date, excepcion.time_start)
                    excepcion_end = datetime.combine(date, excepcion.time_end)

                    # Excluir intervalos de excepción
                    if start_time < excepcion_start:
                        disponibilidad_turno.append((start_time.time(), excepcion_start.time()))

                    start_time = max(start_time, excepcion_end)

            # Si queda tiempo después de excepciones
            if start_time < end_time:
                disponibilidad_turno.append((start_time.time(), end_time.time()))

            # Filtrar citas (appointments) dentro del rango del turno
            for appointment in appointments:
                for service in appointment.services.all():
                    service_duration = EmployeeServices.objects.filter(
                        employee=employee, service=service
                    ).first().duration

                    appointment_start = datetime.combine(date, appointment.time.time())
                    appointment_end = appointment_start + timedelta(minutes=service_duration)

                    # Ajustar disponibilidad según citas
                    disponibilidad_turno = [
                        (s, min(e, appointment_start.time())) for s, e in disponibilidad_turno if e > appointment_start.time()
                    ]
                    disponibilidad_turno += [
                        (max(s, appointment_end.time()), e) for s, e in disponibilidad_turno if s < appointment_end.time()
                    ]

        disponibilidad_completa.extend(disponibilidad_turno)

    if not disponibilidad_completa:
        return "El Artista no tiene disponibilidad en esta fecha."

    return disponibilidad_completa
