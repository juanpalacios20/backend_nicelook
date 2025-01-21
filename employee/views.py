from datetime import date
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from appointment.models import Appointment
from appointment.serializers import appointmentSerializer
from employee_image.models import EmployeeImage
from employee_services.models import EmployeeServices
from employee_services.serializers import employeeServicesSerializer
from review_employee.models import ReviewEmployee
from review_employee.serializers import reviewEmployeeSerializer
from employee.models import Employee
from establisment.models import Establisment
from employee.serializers import EmployeeSerializer
from django.http import JsonResponse
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.db.models import Max
import string
import secrets
import base64
import uuid
from employee_image.models import EmployeeImage
from django.db import transaction
from category.models import Category
from service.models import Service
from schedule.models import Time, TimeException
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from dj_rest_auth.registration.views import SocialLoginView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from datetime import datetime
from receptionist.models import Receptionist
from review_employee.models import ReviewEmployee
from review_employee.serializers import reviewEmployeeSerializer
from receptionist.serializers import receptionistSerializer

# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
  
@api_view(["GET"])  
def professional_reviews(request, professional_id):
    try:
        professional_reviews = ReviewEmployee.objects.filter(employee_id=professional_id)
        
        professional_reviews_serialized = reviewEmployeeSerializer(professional_reviews, many=True)

        return Response(
            {"data": professional_reviews_serialized.data},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": f"Error interno del servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
def setDurationService(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        
        service_id = request.data.get('service_id')
        
        if not service_id:
            return Response({"error": "Service ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        service = Service.objects.get(id=service_id)
        
        employee_service = EmployeeServices.objects.filter(employee=employee, service=service).first()
        
        duration_str = request.data.get('duration')
        if not duration_str:
            return Response({"error": "Duration is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            duration_time = datetime.strptime(duration_str, "%H:%M:%S")
            duration = timedelta(hours=duration_time.hour, minutes=duration_time.minute, seconds=duration_time.second)
        except ValueError:
            return Response({"error": "Invalid duration format. Use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)
        
        employee_service.duration = duration
        employee_service.save()
        
        serializer = employeeServicesSerializer(employee_service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Service.DoesNotExist:
        return Response({"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def employeeAddService(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        
        service_id = request.data.get('service_id')
        establisment_id = employee.establisment.id
        duration_str = request.data.get('duration')

        if not service_id or not duration_str:
            return Response({"error": "Service ID and duration are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            duration_time = datetime.strptime(duration_str, "%H:%M:%S")
            duration = timedelta(hours=duration_time.hour, minutes=duration_time.minute, seconds=duration_time.second)
        except ValueError:
            return Response({"error": "Invalid duration format. Use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)
        
        service = Service.objects.get(id=service_id)
        if service.establisment.id != establisment_id:
            return Response({"error": "El servicio no pertenece al establecimiento indicado."}, status=status.HTTP_400_BAD_REQUEST)

        if not service.state:
            return Response({"error": "El servicio no está activo."}, status=status.HTTP_400_BAD_REQUEST)

        if EmployeeServices.objects.filter(employee=employee, service=service).exists():
            return Response({"message": "El servicio ya está asignado a este empleado."}, status=status.HTTP_400_BAD_REQUEST)

        employee_service = EmployeeServices.objects.create(
            employee=employee,
            service=service,
            duration=duration
        )

        serializer = employeeServicesSerializer(employee_service)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Service.DoesNotExist:
        return Response({"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Actualizar empleado, recibe los datos del empleado por el Body, ejemplo: /update_employee/
@api_view(['PUT'])
def update_employee(request):
    idUser = request.data.get('employee_id')
    if not idUser:
        return Response({'error': 'El ID del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        employee = Employee.objects.get(id=idUser)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        employee = Employee.objects.get(id=idUser)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Datos del Usuario
    name = request.data.get('name', employee.user.first_name)
    last_name = request.data.get('last_name', employee.user.last_name)
    
    # Datos del Empleado
    phone = request.data.get('phone', employee.phone)
    state = request.data.get('state', employee.state)
    
    
    # Validar teléfono
    try:
        phone = validate_phone(phone)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    
    # Actualizar usuario
    employee.user.first_name = name
    employee.user.last_name = last_name
    employee.user.save()
    
    # Actualizar empleado
    employee.phone = phone
    employee.state = state
    employee.save()
    
    return Response({"success": "Empleado actualizado exitosamente"}, status=status.HTTP_200_OK)
    
# Listar empleados, no recibe parámetros, ejemplo: /employee_list/
@api_view(['GET'])
def employee_list(request, establishment_id):
    employees = Employee.objects.filter(establisment_id=establishment_id)
    employees_serialized = EmployeeSerializer(employees, many=True)
    
    receptionists = Receptionist.objects.filter(establisment_id=establishment_id)
    receptionists_serialized = receptionistSerializer(receptionists, many=True)
    
    return Response(
        {"employees": employees_serialized.data, "receptionists": receptionists_serialized.data},
        status=status.HTTP_200_OK
    )

# buscar empleados, recibe un query en el URL, ejemplo: /search_employees/?q=nombre o apellido o ambos
@api_view(['GET'])
def search_employees(request):
    query = request.query_params.get('q', None)
    
    if query:
        # Dividir la consulta en palabras individuales
        query_terms = query.split()
        
        # Crear un Q objeto para filtrar por cada término
        q_objects = Q()
        for term in query_terms:
            q_objects |= Q(first_name__icontains=term) | Q(last_name__icontains=term)
        
        # Buscar usuarios cuyo `first_name` o `last_name` coincidan con cualquiera de los términos
        users = User.objects.filter(q_objects)
        
        # Obtener los empleados que estén relacionados con esos usuarios
        employees = Employee.objects.filter(user__in=users)
        
        if not employees.exists():  # Verifica si no se encontraron empleados
            return Response({"error": "No se encontraron los empleados."}, status=status.HTTP_404_NOT_FOUND)
    else:
        employees = Employee.objects.all()  # Si no hay consulta, devolver todos los empleados
    
    # Serializar los empleados
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)
    
    
# Eliminar empleado, se elimina por la id del usuario en el URL, ejemplo: /delete_employee/?idUser=1
@api_view(['DELETE'])
def delete_employee(request):
    idUser = request.query_params.get('idUser')
    if not idUser:
        return Response({'message': 'El ID del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=idUser)
    except User.DoesNotExist:
        return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return Response({'message': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    employee.delete()
    user.delete()
    
    return Response({'message': 'Empleado eliminado exitosamente'}, status=status.HTTP_200_OK)

# Obtener empleado, recibe el Id del usuario por el URL, ejemplo: /get_employees/?idUser=1
@api_view(['GET'])
def get_employees(request):
    idUser = request.query_params.get('idUser')
    if not idUser:
        return Response({'error': 'El ID del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=idUser)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    employeeSerializer = EmployeeSerializer(employee)
    
    return Response({'employee': employeeSerializer.data}, status=status.HTTP_200_OK)

#validacion del telefono
def validate_phone(phone, country_code="+57"):
    # Si el número no tiene un prefijo '+', añadir el código de país predeterminado
    if not phone.startswith('+'):
        phone = f"{country_code}{phone}"
    
    # Expresión regular para validar el formato
    pattern = r'^\+?1?\d{9,15}$'
    
    # Validar el número
    if not re.match(pattern, phone):
        raise ValidationError("El número de teléfono no es válido.")
    
    return phone  # Devolver el número con el prefijo asignado

def generate_random_password(length=8):
    # Puedes ajustar los caracteres permitidos según tus necesidades
    characters = string.ascii_letters + string.digits + string.punctuation
    # Genera una contraseña aleatoria
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Genera una contraseña aleatoria de 12 caracteres
random_password = generate_random_password(length=8)
   
    
# Crear empleado, recibe los datos del empleado por el Body, ejemplo: /create_employee/
@api_view(['POST'])
def create_employee(request, establisment_id):
    # Datos del Usuario
    name = request.data.get('name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    #password = request.data.get('password', None)

    # Datos del Empleado
    phone = request.data.get('phone')
    especialty = request.data.get('especialty')
    googleid = request.data.get('googleid', None)  # Opcional
    accestoken = request.data.get('accestoken', None)  # Opcional
    token = request.data.get('token', None)  # Opcional

    # Validar campos obligatorios
    if not name or not last_name or not email or not phone or not especialty:
        return Response({'error': 'Los campos nombre, apellido, email, teléfono y especialidad son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar email
    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Formato de email no válido.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar teléfono
    try:
        phone = validate_phone(phone)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        establisment = Establisment.objects.get(id=establisment_id)
    except Establisment.DoesNotExist:
        return Response({'error': 'Establecimiento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


    # Verificar si el email ya está registrado
    if User.objects.filter(email=email).exists():
        return Response({'error': 'El email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar agenda si se proporciona

    # Determinar el siguiente código para el empleado
    next_code = Employee.objects.aggregate(Max('code'))['code__max']

    # Si next_code es None, asignamos el primer código
    if next_code is None:
        next_code = 1
    else:
        next_code = int(next_code) + 1  # Convertir el código a número y aumentar

    # Convertir el código a cadena
    next_code_str = str(next_code)
    

    # Creación de usuario
    username = f"{name}{last_name}{next_code}"
    if User.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya existe.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=random_password, 
                first_name=name, 
                last_name=last_name
            )

            # Creación de empleado
            state = True  # Estado inicial del empleado
            if especialty != "Recepcionista":
                employee = Employee.objects.create(
                    user=user,
                    code=next_code_str,  # Asignar el código secuencial
                    phone=phone,
                    state=state,
                    googleid=googleid,
                    token= token,
                    accestoken=accestoken,
                    establisment=establisment
                )
                especialty, created = Category.objects.get_or_create(name=especialty)
                if created:
                    especialty.save()
                employee.especialty.add(especialty)
            else:
                receptionist = Receptionist.objects.create(
                    user=user,  # Asignar el código secuencial
                    phone=phone,
                    googleid=googleid,
                    token= token,
                    accestoken=accestoken,
                    establisment=establisment
                )
                receptionist.save()
                
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"success": "Empleado creado exitosamente"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def upload_employee_photo(request, establisment_id, employee_id):

    establisment = Establisment.objects.get(id=establisment_id)
    employee = Employee.objects.get(id=employee_id)
    image = EmployeeImage.objects.filter(establishment_id=establisment, employee_id=employee).first()
    #image es el campo que contiene la imagen que quieres subir para el logo
    if image:
            new_image = request.FILES["image"]
            if new_image:
               image.image = new_image.read()
            image.save()
            return JsonResponse({'succes': 'La imagen ha sido actualizada con éxito.'}, status=200)

    image_file = request.FILES["image"]

    if not image_file:
        return JsonResponse({'error': 'La imagen no ha sido proporcionada.'}, status=400)
    #según mi planteamiento, 1 es para el logo y 2 es para el banner

    EmployeeImage.objects.create(
        establishment_id=establisment,
        employee_id=employee,
        image=image_file.read(),
    )

    return JsonResponse({'mensaje': 'La imagen ha sido subida con éxito.'}, status=201)

@api_view(['GET'])
def get_photo(request, establisment_id, employee_id):
    try:
        #filtra el logo del establecimiento
        image_obj = EmployeeImage.objects.filter(establishment_id=establisment_id, employee_id=employee_id ).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada'}, status=404)

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

@api_view(['DELETE'])
def delete_photo(request, establisment_id, employee_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        employee = Employee.objects.get(id=employee_id)
        image_obj = EmployeeImage.objects.filter(establishment_id=establisment, employee_id=employee).first()

        if not image_obj:
            return JsonResponse({'error': 'Imagen no encontrada.'}, status=404)


        image_obj.delete()

        return JsonResponse({'mensaje': 'La imagen se ha elimiando exitosamente.'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establishment not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
@csrf_exempt   
@api_view(['POST'])
def create_time(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        times = Time.objects.filter(employee=employee)

        double_day = request.data.get('double_day')
        time_start_day_one = request.data.get('time_start_day_one')
        time_end_day_one = request.data.get('time_end_day_one')
        date_start = request.data.get('date_start')
        date_end = request.data.get('date_end')
        
        time = Time.objects.filter(
            employee=employee,
            date_start = date_start,
            date_end = date_end
        )
        #condición para que el dia final sea mayor que el dia inicial de manera obligatoria
        if date_start > date_end:
            return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
        #if date_start < datetime.date.today():
            #return Response({"error": "La fecha de inicio debe ser mayor o igual a la fecha actual"}, status=status.HTTP_400_BAD_REQUEST)
        #condición para que el horario final sea mayor que el horario inicial de manera obligatoria
        if time_start_day_one >= time_end_day_one:
            return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
        #condición para que no se puedan crear dos horarios con la misma fecha
        if time:
            return Response({"error": "Ya hay un horario asignado para la fecha seleccionada"}, status=status.HTTP_400_BAD_REQUEST)

        if not time_start_day_one or not time_end_day_one:
            return Response({"error": "El horario del primer turno es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not date_start or not date_end:
            return Response({"error": "La fecha es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)
        
        if double_day:
            time_start_day_two = request.data.get('time_start_day_two')
            time_end_day_two = request.data.get('time_end_day_two')
            
            if not time_start_day_two or not time_end_day_two:
                return Response({"error": "El horario del segundo turno es obligatorio si hay doble turno"}, status=status.HTTP_400_BAD_REQUEST)
            #condición para que el horario final del segundo turno sea mayor 
            #que el horario inicial del segundo turno de manera obligatoria
            if time_start_day_two >= time_end_day_two:
                return Response({"error": "El horario de inicio del segundo turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
            #condición para que el horario inicial del segundo turno sea mayor que el horario inicial del primer turno
            #de manera obligatoria
            if time_start_day_two <= time_start_day_one:
                return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
            #condición para que el horario final del segundo turno sea mayor que el horario final del primer turno
            #de manera obligatoria
            if time_end_day_one >= time_start_day_two:
                return Response({"error": "El horario de fin del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)  
            #condición para que el horario final del segundo turno sea mayor que el horario final del primer turno
            #de manera obligatoria
            if time_end_day_two <= time_end_day_one:
                return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            #condición para que el horario final del segundo turno sea mayor que el horario inicial del primer turno
            #de manera obligatoria
            if time_end_day_two <= time_start_day_one:
                return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
                     
            Time.objects.create(
                employee=employee,
                double_day=double_day,
                time_start_day_one=time_start_day_one,
                time_end_day_one=time_end_day_one,
                time_start_day_two=time_start_day_two,
                time_end_day_two=time_end_day_two,
                date_start = date_start,
                date_end = date_end
            )
        else:
            Time.objects.create(
                employee=employee,
                double_day=double_day,
                time_start_day_one=time_start_day_one,
                time_end_day_one=time_end_day_one,
                date_start = date_start,
                date_end = date_end
            )

        return Response({"success": "Horario creado exitosamente"}, status=status.HTTP_201_CREATED)
    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

@api_view(['PATCH'])
def update_time(request, employee_id):
    try:
        double_day = request.data.get('double_day', False)
        time_start_day_one = request.data.get('time_start_day_one')
        time_end_day_one = request.data.get('time_end_day_one')
        new_time_start_day_one = request.data.get('new_time_start_day_one')
        new_time_end_day_one = request.data.get('new_time_end_day_one')
        new_time_start_day_two = request.data.get('new_time_start_day_two')
        new_time_end_day_two = request.data.get('new_time_end_day_two')
        date_start = request.data.get('date_start')
        date_end = request.data.get('date_end')
        new_date_start = request.data.get('new_date_start')
        new_date_end = request.data.get('new_date_end')
        time = Time.objects.get(employee=employee_id, time_start_day_one=time_start_day_one, time_end_day_one=time_end_day_one, date_start=date_start, date_end=date_end)
        if not time:
            return Response({"error": "Horario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if new_time_start_day_one:
            if new_time_end_day_one:
                if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= datetime.strptime(new_time_end_day_one, '%H:%M').time():
                    return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= time.time_end_day_one:
                    return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            if time.double_day:
                if new_time_start_day_two:
                    if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= datetime.strptime(new_time_start_day_two, '%H:%M').time():
                        return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= time.time_start_day_two:
                        return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
                
                if new_time_end_day_two:
                    if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= datetime.strptime(new_time_end_day_two, '%H:%M').time():
                        return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if datetime.strptime(new_time_start_day_one, '%H:%M').time() >= time.time_end_day_two:
                        return Response({"error": "El horario de inicio del primer turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
        if new_time_end_day_one:
            if new_time_start_day_one:
                if datetime.strptime(new_time_end_day_one, '%H:%M').time() <= datetime.strptime(new_time_start_day_one, '%H:%M').time():
                    return Response({"error": "El horario de fin del primer turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_end_day_one, '%H:%M').time() <= time.time_start_day_one:
                    return Response({"error": "El horario de fin del primer turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            if time.double_day:
                if new_time_start_day_two:
                    if datetime.strptime(new_time_end_day_one, '%H:%M').time() >= time.time_start_day_two:
                        return Response({"error": "El horario de fin del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if datetime.strptime(new_time_end_day_one, '%H:%M').time() >= time.time_start_day_two:
                        return Response({"error": "El horario de fin del primer turno debe ser menor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)     
                if datetime.strptime(new_time_end_day_one, '%H:%M').time() >= time.time_end_day_two:
                    return Response({"error": "El horario de fin del primer turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if new_time_end_day_two :
                        if datetime.strptime(new_time_end_day_one, '%H:%M').time() >= datetime.strptime(new_time_end_day_two, '%H:%M').time():
                            return Response({"error": "El horario de fin del primer turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
        if new_time_start_day_two:
            if new_time_end_day_one:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() <= datetime.strptime(new_time_end_day_one, '%H:%M').time():
                    return Response({"error": "El horario de inicio del segundo turno debe ser mayor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() <= time.time_end_day_one:
                    return Response({"error": "El horario de inicio del segundo turno debe ser menor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            if new_time_end_day_two:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() >= datetime.strptime(new_time_end_day_two, '%H:%M').time():
                    return Response({"error": "El horario de inicio del segundo turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() >= time.time_end_day_two:
                    return Response({"error": "El horario de inicio del segundo turno debe ser menor que el horario de fin del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
            if new_time_start_day_one:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() <= datetime.strptime(new_time_start_day_one, '%H:%M').time():
                    return Response({"error": "El horario de inicio del segundo turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)        
            else:
                if datetime.strptime(new_time_start_day_two, '%H:%M').time() >= time.time_start_day_one:
                    return Response({"error": "El horario de inicio del segundo turno debe ser menor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
        if new_time_end_day_two:
            if new_time_start_day_two:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() <= datetime.strptime(new_time_start_day_two, '%H:%M').time():
                    return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() <= time.time_start_day_two:
                    return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de inicio del segundo turno"}, status=status.HTTP_400_BAD_REQUEST)
            if new_time_start_day_one:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() <= datetime.strptime(new_time_start_day_one, '%H:%M').time():
                    return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() <= time.time_start_day_one:
                    return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de inicio del primer turno"}, status=status.HTTP_400_BAD_REQUEST) 
            if new_time_end_day_one:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() >= datetime.strptime(new_time_end_day_one, '%H:%M').time():
                    return Response({"error": "El horario de fin del segundo turno debe ser menor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if datetime.strptime(new_time_end_day_two, '%H:%M').time() <= time.time_end_day_one:
                    return Response({"error": "El horario de fin del segundo turno debe ser mayor que el horario de fin del primer turno"}, status=status.HTTP_400_BAD_REQUEST)       
        if new_date_start:
            if datetime.strptime(new_date_start, "%Y-%m-%d").date() > time.date_end:
                return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
            if new_date_end:
                if datetime.strptime(new_date_start, "%Y-%m-%d").date() > datetime.strptime(new_date_end, "%Y-%m-%d").date():
                    return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
        if new_date_end:
            if datetime.strptime(new_date_end, "%Y-%m-%d").date() < time.date_start:
                return Response({"error": "La fecha de fin debe ser mayor que la fecha de inicio"}, status=status.HTTP_400_BAD_REQUEST)
            if new_date_start:
                if datetime.strptime(new_date_end, "%Y-%m-%d").date() < datetime.strptime(new_date_start, "%Y-%m-%d").date():
                    return Response({"error": "La fecha de fin debe ser mayor que la fecha de inicio"}, status=status.HTTP_400_BAD_REQUEST)
        time.double_day = double_day if double_day   else time.double_day
        time.time_start_day_one = new_time_start_day_one if new_time_start_day_one else time.time_start_day_one
        time.time_end_day_one = new_time_end_day_one if new_time_end_day_one else time.time_end_day_one
        time.time_start_day_two = new_time_start_day_two if new_time_start_day_two else time.time_start_day_two
        time.time_end_day_two = new_time_end_day_two if new_time_end_day_two else time.time_end_day_two
        time.date_start = new_date_start if new_date_start else time.date_start
        time.date_end = new_date_end if new_date_end else time.date_end
        time.save()

        return Response({"success": "Horario actualizado exitosamente"}, status=status.HTTP_200_OK)
    except Time.DoesNotExist:
        return Response({"error": "Horario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['DELETE'])
def delete_time(request, employee_id):
    try:
        date = request.query_params.get('date')
        employee = Employee.objects.get(id=employee_id)
        if not date:
            return Response({'error': 'La fecha del dia no laboral es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        if not employee:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        exception = TimeException.objects.filter(employee=employee, date_start=date, date_end=date, time_start=datetime.strptime("00:00", '%H:%M').time(), time_end=datetime.strptime("23:00", '%H:%M').time()).first()
        if exception:
            return Response({'error': 'Dia no laboral ya creado'}, status=status.HTTP_400_BAD_REQUEST)
        TimeException.objects.create(
            employee = employee,
            date_start = date,
            date_end = date,
            reason = "Motivos personales",
            time_start = datetime.strptime("00:00", '%H:%M').time(),
            time_end = datetime.strptime("23:00", '%H:%M').time()
        )   
         
        return Response({"success": "Dia no laboral creado exitosamente"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_time(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        times = Time.objects.filter(employee=employee)

        # Preparamos los datos a devolver
        times_data = []
        for time in times:
            time_data = {
                'id': time.id,
                'double_day': time.double_day,
                'time_start_day_one': time.time_start_day_one,
                'time_end_day_one': time.time_end_day_one,
                #'working_days': time.working_days,
                'time_start_day_two': time.time_start_day_two,
                'time_end_day_two': time.time_end_day_two,
            }
            times_data.append(time_data)  # Agregar a la lista

        return Response(times_data, status=status.HTTP_200_OK)  # Devolver la lista completa

    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_exception(request, employee_id):
    try:
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        reason = request.data.get('reason')
        time_start = request.data.get('time_start')
        time_end = request.data.get('time_end')
        employee = Employee.objects.get(id=employee_id)
        exception = TimeException.objects.filter(
            employee_id = employee_id,
            date_start = start_date,
            date_end = end_date,
            time_start = time_start,
            time_end = time_end
        )
        
        exception2 = TimeException.objects.filter(
            employee_id = employee_id,
            date_start = start_date,
            date_end = end_date
        )
        
        if not start_date or not time_start or not time_end:
            return Response({"error": "Los campos start_date, time_start y time_end son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
        if exception:
            return Response({"error": "Ya hay una excepcion asignada para la fecha y hora seleccionada"}, status=status.HTTP_400_BAD_REQUEST) 
        
        contador = 0
        for exception in exception2:
            contador += 1
        if contador == 2:
            return Response({"error": "Limite de excepciones alcanzado", "limit_exceptions": True}, status=status.HTTP_400_BAD_REQUEST)
        
        if start_date > end_date:
            return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
        #if start_date < datetime.date.today():
            #return Response({"error": "La fecha de inicio debe ser mayor o igual a la fecha actual"}, status=status.HTTP_400_BAD_REQUEST)

        if time_start >= time_end:
            return Response({"error": "La hora de inicio debe ser menor que la hora de fin"}, status=status.HTTP_400_BAD_REQUEST)
        if end_date and reason:
            TimeException.objects.create(
                employee=employee,
                date_start = start_date,
                date_end = end_date if end_date else start_date,
                reason = reason if reason else "Motivos personales",
                time_start = time_start,
                time_end = time_end,
            )
        return Response({"success": "Excepcion de horario creado exitosamente"}, status=status.HTTP_201_CREATED)
    
    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['PATCH'])
def update_exception(request, employee_id):
    try:
        #en este metodo es necesario enviar las fechas de inicio y final y las horas de inicio y final para actualizar la excepcion
        #si se va a actualizar la fecha u hora debe enviar un new_date_start o new_date_end o new_time_start o new_time_end
        #según sea el caso
        date_start = request.data.get('date_start')
        date_end = request.data.get('date_end')
        reason = request.data.get('reason')
        time_start = request.data.get('time_start')
        time_end = request.data.get('time_end')
        new_date_start = request.data.get('new_date_start')
        new_date_end = request.data.get('new_date_end')
        new_time_start = request.data.get('new_time_start')
        new_time_end = request.data.get('new_time_end')
        if not date_start and not date_end:
            return Response({"error": "Los campos date_start y date_end son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
        if new_date_start:
            if not new_date_end:
                if new_date_start > date_end:
                    return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if new_date_end is not None:
                    if new_date_start > new_date_end:
                        return Response({"error": "La fecha de inicio debe ser menor que la fecha de fin"}, status=status.HTTP_400_BAD_REQUEST)
        if new_date_end:
            if not new_date_start:
                if new_date_end < date_start:
                    return Response({"error": "La fecha de fin debe ser mayor que la fecha de inicio"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if new_date_start is not None:
                    if new_date_end < new_date_start:
                        return Response({"error": "La fecha de fin debe ser mayor que la fecha de inicio"}, status=status.HTTP_400_BAD_REQUEST)
        if new_time_start:
            if not new_time_end:
                if new_time_start > time_end:
                    return Response({"error": "La hora de inicio debe ser menor que la hora de fin"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if new_time_end is not None:
                    if new_time_start > new_time_end:
                        return Response({"error": "La hora de inicio debe ser menor que la hora de fin"}, status=status.HTTP_400_BAD_REQUEST)
        if new_time_end:
            if not new_time_start:
                if new_time_end < time_start:
                    return Response({"error": "La hora de fin debe ser mayor que la hora de inicio"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if new_time_start is not None:
                    if new_time_end < new_time_start:
                        return Response({"error": "La hora de fin debe ser mayor que la hora de inicio"}, status=status.HTTP_400_BAD_REQUEST)
        exception = TimeException.objects.get(employee=employee_id, date_start=date_start, date_end=date_end)
        if not new_date_start is None:
            exception.date_start = new_date_start
            exception.date_end = new_date_end
        if not reason is None:
            exception.reason = reason
        if not new_time_start is None:
            exception.time_start = time_start
        if not new_time_end is None:
            exception.time_end = time_end
        exception.save()
        return Response({"success": "Horario actualizado exitosamente"}, status=status.HTTP_200_OK)
    except TimeException.DoesNotExist:
        return Response({"error": "Horario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_exception(request, employee_id):
    try:
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        time_start = request.query_params.get('time_start')
        time_end = request.query_params.get('time_end')
        exception = TimeException.objects.filter(employee=employee_id, date_start=date_start, date_end=date_end, time_start=time_start, time_end=time_end).first()
        exception.delete()
        return Response({"success": "Horario eliminado exitosamente"}, status=status.HTTP_200_OK)
    except TimeException.DoesNotExist:
        return Response({"error": "Horario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def history_appointments(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        day = int(request.GET.get('day'))
        if not year or not month or not  day:
            return Response({'error': 'Year, month and day are required parameters'}, status=status.HTTP_400_BAD_REQUEST)
        appointments = Appointment.objects.filter(employee=employee,date__year=year,date__month=month,date__day=day).filter(Q(estate__icontains='Completada') | Q(estate__icontains='Cancelada')
)
        if not appointments.exists(): 
            return Response({'error': "Appointments doesn't exist" },status=status.HTTP_404_NOT_FOUND)
        info_appoiments = []
        total_earnings = 0
        for appointment in appointments:
            services = []
            total = 0
            review = ReviewEmployee.objects.filter(autor=appointment.client, employee=employee, appointment=appointment.id).first()
            rSerializer = reviewEmployeeSerializer(review)
            for service in appointment.services.all():
                total += (service.price - (service.price * service.commission))
                services.append({
                    'name': service.name,
                })
            if appointment.estate == "Completada":
                total_earnings += total
            info_appoiments.append({
                'id': appointment.id,
                'time': appointment.time.strftime("%H:%M"),
                'services': services,
                'total': total,
                'method': appointment.method,
                'state': appointment.estate,
                'client': appointment.client.user.first_name + ' ' + appointment.client.user.last_name,
                'rating': rSerializer.data['rating'],
            })
        return Response({"appointments": info_appoiments, "earnings": total_earnings}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def schedule_employee(request, employee_id):
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        day = int(request.GET.get('day'))
        appointments_date = date(year, month, day) 
        if not year or not month or not  day:
            return Response({'error': 'Year, month and day are required parameters'}, status=status.HTTP_400_BAD_REQUEST)
        appointments = Appointment.objects.filter(date = appointments_date, employee_id = employee_id, estate__icontains='Pendiente')
        if not appointments.exists():
            return Response({'error': "Appointments doesn't exist" },status=status.HTTP_404_NOT_FOUND)
        info_appoiments = []
        for appointment in appointments:
            services = []
            total = 0
            for service in appointment.services.all():
                total += service.price
                services.append({
                    'name': service.name,
                })
            info_appoiments.append({
                'id': appointment.id,
                'time': appointment.time.strftime("%H:%M"),
                'services': services,
                'total': total,
                'state': appointment.estate,
                'method': appointment.method,
                'client': appointment.client.user.first_name + ' ' + appointment.client.user.last_name
            })
        return Response({"appointments": info_appoiments}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Employee
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config

class EmployeeLogin(APIView):
    def post(self, request, *args, **kwargs):
        auth_code = request.data.get('auth_code')

        if not auth_code:
            return Response({'error': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # URL para obtener los tokens de Google
        token_url = 'https://oauth2.googleapis.com/token'

        # Datos necesarios para hacer la solicitud POST a Google para obtener los tokens
        data = {
            'code': auth_code,  # El authorization code que recibiste del frontend
            'client_id': config("CLIENT_ID"),  # Tu client_id de Google
            'client_secret': config("CLIENTE_SECRET"),  # Tu client_secret de Google
            'redirect_uri': "https://nicelook.vercel.app",  # Tu URI de redirección (debe coincidir con la configuración en Google)
            'grant_type': 'authorization_code',  # Tipo de flujo
        }

        # Realizar la solicitud POST para obtener los tokens
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            return Response({'error': 'Failed to exchange authorization code for tokens', 'details': response.json()}, status=status.HTTP_400_BAD_REQUEST)

        # Si la solicitud es exitosa, obtener los tokens
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')


        if not access_token:
            return Response({'error': 'Access token not found in the response'}, status=status.HTTP_400_BAD_REQUEST)

        # Usar el access_token para obtener la información del usuario desde Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
        
        if user_info_response.status_code != 200:
            return Response({'error': 'Failed to retrieve user information from Google'}, status=status.HTTP_400_BAD_REQUEST)

        # Datos del usuario
        user_data = user_info_response.json()
        email = user_data.get('email')
        google_id = user_data.get('id')
        first_name = user_data.get('given_name')
        last_name = user_data.get('family_name')

        if not user_data.get('verified_email', False):
            return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el usuario ya existe en la base de datos
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        employee = Employee.objects.filter(user=user).first()
        if employee:
            if employee.state == False:
                return Response({'error': 'No estas activo/a en la lista de profesionales del establecimiento'}, status=status.HTTP_400_BAD_REQUEST)
            employee.token = refresh_token
            employee.accestoken = access_token
            employee.googleid = google_id
            employee.save()

            # Generar el token JWT para el usuario
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['first_name'] = user.first_name
            refresh['last_name'] = user.last_name
            refresh['google_id'] = google_id

            # Responder con el JWT y los datos del usuario
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'establishment_id': employee.establisment.id,
                'id_employee': employee.id,
                'isArtist': True
            }, status=status.HTTP_200_OK)
        
        receptionist = Receptionist.objects.filter(user=user).first()
        if receptionist:
            if receptionist.state == False:
                return Response({'error': 'No estas activo/a en la lista de profesionales del establecimiento'}, status=status.HTTP_400_BAD_REQUEST)
            receptionist.token = refresh_token
            receptionist.accestoken = access_token
            receptionist.googleid = google_id
            receptionist.save()

            # Generar el token JWT para el usuario
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['first_name'] = user.first_name
            refresh['last_name'] = user.last_name
            refresh['google_id'] = google_id

            # Responder con el JWT y los datos del usuario
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'establishment_id': receptionist.establisment.id,
                'id_receptionist': receptionist.id,
                'isArtist': False,
            }, status=status.HTTP_200_OK)
        
        if not receptionist and not employee:
            return Response({'error': 'No te hemos encontrado en la lista de profesionales de el establecimiento, contacta con ellos para resolver el problema'}, status=status.HTTP_404_NOT_FOUND)


