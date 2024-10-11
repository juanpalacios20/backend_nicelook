import datetime

from product.models import Product
from .models import Establisment
import base64
import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from service.models import Service
from appointment.models import Appointment
from employee.models import Employee
from employee_services.models import EmployeeServices
from product_payment.models import Product_payment

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
        print(year, month, day)
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
        print(establisment)
        print("hasta aqui silvo")
        # Filtra las citas por el establecimiento, estado, año y mes
        appointments = Appointment.objects.filter(
            establisment=establisment,
            estate__icontains=state,
            date__year=year
        )
        print("aqui no silvo")
        print(appointments)
        if not appointments.exists():
            return JsonResponse({'error': 'No appointments found'}, status=404) 
        
        for appointment in appointments:
            employee = Employee.objects.get(id=appointment.employee.id)
            appointment_services = []  
            total = 0
            profit_employee = 0
            
            for service in appointment.services.all():
                profit_establisment = service.price * (service.commission / 100)
                profit_employee += service.price - profit_establisment
                total += profit_establisment
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
                    'client': appointment.client.user.username,
                    'total': appointment.payment.total,
                    'date': appointment.date,
                    'employee': employee.user.username,
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
def get_filter_payments_product(request, establisment_id):
    try:
        # Obtener año y mes de la consulta
        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')
                
        product_list = [] 
        profit_months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_day = 0

        if not year or not month or not day:
            return JsonResponse({'error': 'Year, month and day are required parameters'}, status=400)

        # Buscar el establecimiento
        establisment = Establisment.objects.get(id=establisment_id)

        # Filtrar los pagos de productos por establecimiento, estado, año y mes
        productPayments = Product_payment.objects.filter(
            establisment=establisment,
            state=False,
            date__year=year
        )
        
        if not productPayments.exists():
            return JsonResponse({'error': 'No product payments found'}, status=404)  
        
        # Iterar sobre los pagos de productos
        for productpayment in productPayments:
            products_info = [] 
            total = 0
            
            for product in productpayment.products.all():
                discount = (product.price * (product.discount / 100))
                discount_price = product.price - discount  # Precio con descuento
                profit = (discount_price - product.purchase_price) * productpayment.quantity 
                total += profit
                products_info.append({
                        'product_name': product.name,
                        'product_price': product.price,
                        'discount_price': discount,
                        'profit': profit,
                        'quantity': productpayment.quantity,
                        'brand': product.brand,
                        'estate': product.estate
                    })
                
            if productpayment.date.day == int(day) and productpayment.date.month == int(month) and productpayment.date.year == int(year):
                total_day += profit
                product_list.append({
                    'payment_id': productpayment.id,
                    'client': productpayment.client.user.username,
                    'total': total,
                    'date': productpayment.date,
                    'method': productpayment.method,
                    'quantity': productpayment.quantity,
                    'products': products_info
                })
        profit_months[int(productpayment.date.month)-1] += total 
            # Añadir la información del pago y los productos a la lista general
        
        # Devolver la ganancia del establecimiento y la lista de productos con los detalles
        profit_year = sum(profit_months)
        return JsonResponse({
            'ganancia_meses': profit_months[int(month)-1],
            'ganancia_año': profit_year,
            'ganancia_establecimiento': total_day,
            'product_payments': product_list
        }, status=200)

    except Establisment.DoesNotExist:
        return JsonResponse({'error': 'No establisment found'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': "hola"}, status=500)
