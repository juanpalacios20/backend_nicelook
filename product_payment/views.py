from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse
from client.models import Client
from establisment.models import Establisment
from product.models import Product
from productPaymentDetail.models import ProductPaymentDetail
import product_payment
from .models import Product_payment
from .serializers import ProductPaymentSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
class productPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPaymentSerializer
    queryset =Product_payment.objects.all()
    
@api_view(['POST'])
def create_product_payment(request, establisment_id, client_id):
    establisment = Establisment.objects.get(id=establisment_id)
    client = Client.objects.get(id=client_id)
    products = request.data.get('products', []	) #necesito que esto sea un arreglo o un json
    method = request.data.get('method')
    date = request.data.get('date')
    
    if not establisment_id and not client_id:
        return JsonResponse({'error': 'Establecimiento y cliente no proporcionados'}, status=400)
    if not establisment:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)
    if not client:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
    if not products:
        return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
    if not method:
        return JsonResponse({'error': 'No se proporciono el metodo de pago'}, status=400)
    if not date:
        return JsonResponse({'error': 'No se proporcionaron datos'}, status=400)
    
    try:
        payment = Product_payment.objects.create(
            establisment=establisment,
            client=client,
            state = True, #al ser true significa que la compra está en modo carrito
            method = method,
            date = date
        )
        
        for product in products:
            discountt = 0
            product_id = product.get('id')
            quantity = product.get('quantity')
            product_pay = Product.objects.get(id=product_id)
            ProductPaymentDetail.objects.create(
                payment=payment,
                product=product_pay,
                quantity=quantity
            )
            product_pay.quantity -= quantity
            product_pay.save()
            discountt += (product_pay.price * product_pay.discount)#/100
        payment.discount = discountt
        payment.save()
        
        return JsonResponse({'mensaje': 'Compra creada exitosamente'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
def details (request, payment_id):
    try:
        payment = Product_payment.objects.get(id=payment_id)
        serializer = ProductPaymentSerializer(payment)
        return JsonResponse(serializer.data, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@api_view(['DELETE'])
def cancel_payment(request, payment_id):
    try:
        payment = Product_payment.objects.get(id=payment_id)
        payment.delete()
        return JsonResponse({'mensaje': 'Compra cancelada exitosamente'}, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def send_email_details(request):
    asunto = 'IMPORTANTE'
    mensaje = 'Ya que ha ingresado a xnxx, nos hemos expropiado del proyecto nicelook, si desea recuperarlo debera depositar 1000000 al siguiente numero de nequi 3161747842'
    remitente = settings.EMAIL_HOST_USER
    destinatarios = ['sebastian.hernandez.scarpetta@correounivalle.edu.co']

    send_mail(asunto, mensaje, remitente, destinatarios)
    return JsonResponse({'mensaje': 'Email enviado'}, status=200)