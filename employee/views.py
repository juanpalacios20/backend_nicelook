from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from employee_image.models import EmployeeImage
from schedule.models import Schedule
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
from employee_image.models import EmployeeImage
from django.db import transaction
from category.models import Category
# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    
    
# Actualizar empleado, recibe los datos del empleado por el Body, ejemplo: /update_employee/
@api_view(['PUT'])
def update_employee(request):
    idUser = request.data.get('idUser')
    if not idUser:
        return Response({'error': 'El id del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=idUser)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Datos del Usuario
    name = request.data.get('name', user.first_name)
    last_name = request.data.get('last_name', user.last_name)
    
    # Datos del Empleado
    phone = request.data.get('phone', employee.phone)
    state = request.data.get('state', employee.state)
    
    
    # Validar teléfono
    try:
        phone = validate_phone(phone)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    
    # Actualizar usuario
    user.first_name = name
    user.last_name = last_name
    user.save()
    
    # Actualizar empleado
    employee.phone = phone
    employee.state = state
    employee.save()
    
    return Response({"success": "Empleado actualizado exitosamente"}, status=status.HTTP_200_OK)
    
# Listar empleados, no recibe parámetros, ejemplo: /employee_list/
@api_view(['GET'])
def employee_list(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)

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
        return Response({'message': 'El id del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
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
        return Response({'error': 'El id del usuario es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    
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
    especialty = request.data.get('especialty', [])  # Lista de especialidades (IDs)
    schedule = request.data.get('schedule', None)  # Opcional
    googleid = request.data.get('googleid', None)  # Opcional
    accestoken = request.data.get('accestoken', None)  # Opcional
    token = request.data.get('token', None)  # Opcional

    # Validar campos obligatorios
    if not name or not last_name or not email or not phone or not especialty:
        return Response({'error': 'Los campos nombre, apellido, email, teléfono y especialidad son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar email
    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Formato de email no válido'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar teléfono
    try:
        phone = validate_phone(phone)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        establisment = Establisment.objects.get(id=establisment_id)
    except Establisment.DoesNotExist:
        return Response({'error': 'Establecimiento no encontrado'}, status=status.HTTP_404_NOT_FOUND)


    # Verificar si el email ya está registrado
    if User.objects.filter(email=email).exists():
        return Response({'error': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

    # Validar agenda si se proporciona
    if schedule:
        try:
            schedule = Schedule.objects.get(id=schedule)
        except Schedule.DoesNotExist:
            return Response({'error': 'Agenda no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    # Determinar el siguiente código para el empleado
    next_code = Employee.objects.aggregate(Max('code'))['code__max'] or 0
    next_code += 1  # Incrementar para asignar un nuevo código
    

    # Creación de usuario
    username = f"{name}{last_name}{next_code}"
    if User.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

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
            employee = Employee.objects.create(
                user=user,
                code=next_code,  # Asignar el código secuencial
                phone=phone,
                state=state,
                schedule=schedule if schedule is not None else None,  # Puede ser None
                googleid=googleid,
                token=token,
                accestoken=accestoken,
                establisment=establisment
            )

            # Asignar especialidades
            especialties = Category.objects.filter(id__in=especialty)
            employee.especialty.set(especialties)

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
            return JsonResponse({'succes': 'The photo has been update successfully'}, status=200)

    image_file = request.FILES["image"]

    if not image_file:
        return JsonResponse({'error': 'The image has not been provided'}, status=400)
    #según mi planteamiento, 1 es para el logo y 2 es para el banner

    EmployeeImage.objects.create(
        establishment_id=establisment,
        employee_id=employee,
        image=image_file.read(),
    )

    return JsonResponse({'mensaje': 'The photo has been uploaded successfully'}, status=201)

@api_view(['GET'])
def get_photo(request, establisment_id, employee_id):
    try:
        #filtra el logo del establecimiento
        image_obj = EmployeeImage.objects.filter(establishment_id=establisment_id, employee_id=employee_id ).first()

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

@api_view(['DELETE'])
def delete_photo(request, establisment_id, employee_id):
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        employee = Employee.objects.get(id=employee_id)
        image_obj = EmployeeImage.objects.filter(establishment_id=establisment, employee_id=employee).first()

        if not image_obj:
            return JsonResponse({'error': 'Photo not found'}, status=404)


        image_obj.delete()

        return JsonResponse({'mensaje': 'Photo sucssefuly deleted'}, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'Establishment not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)