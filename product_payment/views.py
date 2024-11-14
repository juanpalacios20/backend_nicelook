from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse
from client.models import Client
from establisment.models import Establisment
from product.models import Product
from product.serializers import productSerializer
from productPaymentDetail.models import ProductPaymentDetail
import product_payment
from .models import Product_payment
from .serializers import ProductPaymentSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
class productPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPaymentSerializer
    queryset =Product_payment.objects.all()
    
@api_view(['POST'])
def create_product_payment(request, establisment_id, client_id):
    #Este metodo es para meter todos los productos al carrito al mismo tiempo
    establisment = Establisment.objects.get(id=establisment_id)
    client = Client.objects.get(id=client_id)
    products = request.data.get('products', []) #necesito que esto sea un arreglo o un json
    date = request.data.get('date')
    
    if not establisment_id and not client_id:
        return JsonResponse({'error': 'Establecimiento y cliente no proporcionados'}, status=400)
    if not establisment:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)
    if not client:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
    if not products:
        return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
    if not date:
        return JsonResponse({'error': 'No se proporcionaron datos'}, status=400)
    
    try:
        payment = Product_payment.objects.create(
            establisment=establisment,
            client=client,
            state = True, #al ser true significa que la compra está en modo carrito
            method = " ",
            date = date
        )
        
        for product in products:
            discountt = 0
            product_code = product.get('code')
            quantity = product.get('quantity')
            product_pay = Product.objects.get(id=product_code)
            ProductPaymentDetail.objects.create(
                payment=payment,
                product=product_pay,
                quantity=quantity
            )
            #product_pay.quantity -= quantity
            #product_pay.save()
            discountt += (product_pay.price * product_pay.discount)#/100
        payment.discount = discountt
        payment.save()
        
        return JsonResponse({'mensaje': 'Compra creada exitosamente'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['POST'])
def create_product_payment_option2(request, establisment_id, client_id):
    #Este metodo es para meter todos los productos al carrito 1 por 1
    establisment = Establisment.objects.get(id=establisment_id)
    client = Client.objects.get(id=client_id)
    data = request.data
    product_code = data.get('code')
    product_pay = Product.objects.get(id=product_code)
    if not establisment_id and not client_id:
        return JsonResponse({'error': 'Establecimiento y cliente no proporcionados'}, status=400)
    if not establisment:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)
    if not client:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
    if not product_code:
        return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
    payment = Product_payment.objects.filter(client=client, state=True).first()
    paymentD = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
    if payment:
            try:
                if paymentD:
                    paymentD.quantity += 1
                    paymentD.save()
                else:
                    ProductPaymentDetail.objects.create(
                    payment=payment,
                    product=product_pay,
                    quantity=1.0
                    )
                #product_pay.quantity -= 1
                #product_pay.save()
                discountt = (product_pay.price * product_pay.discount)#/100        
                payment.discount = discountt
                payment.save()
                return JsonResponse({'mensaje': 'Compra creada exitosamente'}, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    try:
        date = request.data.get('date')
        if not date:
            return JsonResponse({'error': 'No se proporcionaron datos'}, status=400)
        payment = Product_payment.objects.create(
            establisment=establisment,
            client=client,
            state = True, #al ser true significa que la compra está en modo carrito
            method = " ",
            date = date
        )
        discountt = 0
        product_pay = Product.objects.get(id=product_code)
        ProductPaymentDetail.objects.create(
                payment=payment,
                product=product_pay,
                quantity=1.0
            )
        #product_pay.quantity -= 1
        #product_pay.save()
        discountt += (product_pay.price * product_pay.discount)#/100
        payment.discount = discountt
        payment.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@api_view(['PATCH'])
def agregate_product(request, payment_id):
    #Este metodo es para agregar un producto al carrito si se utiliza la opcion de agregar todos los productos al tiempo
    try:
        payment = Product_payment.objects.get(id=payment_id)
        data = request.data
        product_code = data.get('code')
        if not payment:
            return JsonResponse({'error': 'Compra no encontrada'}, status=404)
        if not product_code:
            return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
        product_pay = Product.objects.get(code=product_code)
        if payment.state == False:
            return JsonResponse({'error': 'Compra no encontrada'}, status=404)
        paymentD = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
        if paymentD:
            paymentD.quantity += 1.0
            product_pay.quantity -= 1
            product_pay.save()
            paymentD.save()
            discountt = (product_pay.price * product_pay.discount)#/100
            payment.discount += discountt
            payment.save()
            return JsonResponse({'mensaje': 'Producto agregado exitosamentee'}, status=201)
        ProductPaymentDetail.objects.create(
            payment=payment,
            product=product_pay,
            quantity=1.0
                )
        #product_pay.quantity -= 1.0
        #product_pay.save()
        discountt = (product_pay.price * product_pay.discount)#/100
        payment.discount += discountt
        payment.save()
        return JsonResponse({'mensaje': 'Producto agregado exitosamente'}, status=201)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@api_view(['GET'])
def details (request, payment_id):
    #Este metodo es para ver los detalles de la compra
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
    #Este metodo es para cancelar la compra
    try:
        payment = Product_payment.objects.get(id=payment_id)
        payment.delete()
        return JsonResponse({'mensaje': 'Compra cancelada exitosamente'}, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['DELETE'])
def  delete_product_of_payment(request, payment_id):
    #Este metodo es para eliminar un producto (cantidad) de la compra
    try:
        payment = Product_payment.objects.get(id=payment_id)
        data = request.data
        product_code = data.get('code')
        if not payment:
            return JsonResponse({'error': 'Compra no encontrada'}, status=404)
        if not product_code:
            return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
        product_pay = Product.objects.get(code=product_code)
        if payment.state == False:
            return JsonResponse({'error': 'Compra no encontrada'}, status=404)
        paymentD = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
        if not paymentD:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        paymentD.quantity -= 1.0
        if paymentD.quantity == 0:
            paymentD.delete()
        return JsonResponse({'error': 'Producto eliminado'}, status=404)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@api_view(['POST'])
def complete_payment(request, payment_id):
    #Este metodo es para completar la compra y enviar la factura con los detalles
    try:
        payment = Product_payment.objects.get(id=payment_id)
        payment.state = False
        payment.save()
        
        product = payment.products.all()
        products_info = []
        for p in product:
            product_pay = Product.objects.get(id=p.id)
            product_pay.quantity -= p.quantity
            product_pay.save()
            detailsP = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
            products_info.append({
                "name": product_pay.name,
                "quantity": detailsP.quantity,
                "price": product_pay.price * detailsP.quantity
            })

        # Formatear la información de productos en una cadena
        products_details = ""
        for item in products_info:
            products_details += f"- {item['name']}: {item['quantity']} x ${item['price']}\n"

        asunto = f'Hola, {payment.client.user.first_name}, aquí está tu factura'
        mensaje = f"""Esta es la información de tu compra:

Establecimiento: {payment.establisment.name}
Cliente: {payment.client.user.first_name} {payment.client.user.last_name}
Fecha: {payment.date}
Total: ${payment.total_price}
Descuento: ${payment.discount}

Productos:
{products_details}

Ya puedes pasar a retirar tu compra en el establecimiento.

Gracias por preferirnos,
Nicelook"""

        remitente = settings.EMAIL_HOST_USER
        destinatarios = [payment.client.user.email]

        send_mail(asunto, mensaje, remitente, destinatarios)
        return JsonResponse({'mensaje': 'Compra completada exitosamente'}, status=200)

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

@api_view(["GET"])
#@permission_classes([IsAuthenticated])  # Descomentar si necesitas autenticación
def filter_products(request):
    name = request.query_params.get("name")
    product = Product.objects.filter(name__icontains=name)
    serializer = productSerializer(product, many=True)
    
    try: 
        name = request.query_params.get("name")
        product = Product.objects.filter(name__icontains=name)
        serializer = productSerializer(product, many=True)
        
        return Response(
            {"products": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": f"Error en el servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )