from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from schedule.models import Schedule
from employee.models import Employee
from employee.serializers import EmployeeSerializer
from django.contrib.auth.models import User
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.db.models import Max
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
@permission_classes([IsAuthenticated])
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
   
    
# Validacion de la contraseña
def validate_password(password):
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("La contraseña debe contener al menos un número.")
    if not re.search(r'[\W_]', password):
        raise ValidationError("La contraseña debe contener al menos un carácter especial.")
    
# Crear empleado, recibe los datos del empleado por el Body, ejemplo: /create_employee/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employee(request):
    #Datos del Usuario
    name = request.data.get('name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    #Datos del Empleado
    code = request.data.get('code')
    phone = request.data.get('phone')
    especialty = request.data.get('especialty')
    schedule = request.data.get('schedule')
    googleid = request.data.get('googleid', None)
    accestoken = request.data.get('accestoken', None)
    token = request.data.get('token', None)
    
     # Validar campos obligatorios
    if not name or not last_name or not email or not password or not phone or not especialty or not schedule:
        return Response({'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    # Validar contraseña
    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si el email ya está registrado
    if User.objects.filter(email=email).exists():
        return Response({'error': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar agenda
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
    
    user = User.objects.create_user(username=username, email=email, password=password, first_name=name, last_name=last_name)

    # Creación de empleado
    state = True  # Estado inicial del empleado
    employee = Employee.objects.create(
        user=user,
        code=next_code,  # Asignar el código secuencial
        phone=phone,
        state=state,
        especialty=especialty,
        schedule=schedule,
        googleid=googleid,
        token=token,
        accestoken=accestoken
    )

    # Guardar empleado
    employee.save()

    return Response({"success": "Empleado creado exitosamente"}, status=status.HTTP_201_CREATED)
        


    
    
    

    
