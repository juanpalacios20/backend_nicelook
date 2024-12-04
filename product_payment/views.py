import base64
from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse
from Image_product.models import ImageProduct
from client.models import Client
from establisment.models import Establisment
from product.models import Product
from product.serializers import productSerializer
import productPaymentDetail
from productPaymentDetail.models import ProductPaymentDetail
import product_payment
from review_product.models import ReviewProduct
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
    print(client.user.first_name)
    product_code = request.data.get('code')
    print(product_code)
    print("hola")
    product_pay = Product.objects.get(code=product_code)
    if not establisment_id and not client_id:
        return JsonResponse({'error': 'Establecimiento y cliente no proporcionados'}, status=400)
    if not establisment:
        return JsonResponse({'error': 'Establecimiento no encontrado'}, status=404)
    if not client:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
    if not product_code:
        return JsonResponse({'error': 'No se proporcionaron productos'}, status=400)
    if not product_pay:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    payment = Product_payment.objects.filter(client=client, state=True).first()
    paymentD = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
    
    if product_pay.quantity == 0:
        return JsonResponse({'error': 'Existencias agotadas'}, status=404)
    
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
                discountt = (product_pay.price * product_pay.discount)#/100        
                payment.discount = discountt
                payment.save()
                product_pay.quantity -= 1
                product_pay.save()
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
            method = "Efectivo",
            date = date
        )
        print(client.user.first_name)
        discountt = 0
        product_pay = Product.objects.get(id=product_code)
        ProductPaymentDetail.objects.create(
                payment=payment,
                product=product_pay,
                quantity=1.0
            )
        product_pay.quantity -= 1
        product_pay.save()
        discountt += (product_pay.price * product_pay.discount)#/100
        payment.discount = discountt
        payment.save()
        return JsonResponse({'mensaje': 'Compra creada exitosamente'}, status=201)
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
            discountt = (product_pay.price * product_pay.discount)/100
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
        discountt = (product_pay.price * product_pay.discount)/100
        payment.discount += discountt
        payment.save()
        return JsonResponse({'mensaje': 'Producto agregado exitosamente'}, status=201)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@api_view(['GET'])
def details (request):
    #Este metodo es para ver los detalles de la compra
    try:
        data = []
        payment = Product_payment.objects.filter(state=True).first()
        details = ProductPaymentDetail.objects.filter(payment=payment)
        for d in details:
            image = ImageProduct.objects.filter(id_product=d.product).first()
            if not image:
                image_base64_url = None
            else:
                image_binaria = image.image
                image_base64 = base64.b64encode(image_binaria).decode('utf-8')
                mime_type = "image/jpeg"
                image_base64_url = f"data:{mime_type};base64,{image_base64}"
            discount = (d.product.price * (d.product.discount/100))
            data.append({
                'name': d.product.name,
                'image': image_base64_url,
                'description': d.product.description,
                'price': d.product.price,
                'quantity': d.quantity,
                'code': d.product.code,
                'discount': discount,
                'discount_total': discount * d.quantity,
                'price_total': d.product.price * d.quantity,
                'price_final': (d.product.price * d.quantity) - discount
            })
        return JsonResponse(data, safe=False, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@api_view(['DELETE'])
def cancel_payment(request):
    #Este metodo es para cancelar la compra
    try:
        payment = Product_payment.objects.filter(state=True).first()
        print("hola")
        detail = ProductPaymentDetail.objects.filter(payment=payment)
        for d in detail:
            print("hola")
            product_pay = Product.objects.get(id=d.product.id)
            print("hola")
            product_pay.quantity += d.quantity
            product_pay.save()
        payment.delete()
        return JsonResponse({'mensaje': 'Compra cancelada exitosamente'}, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['DELETE'])
def  delete_product_of_payment(request):
    #Este metodo es para eliminar un producto (cantidad) de la compra
    try:
        payment = Product_payment.objects.filter(state=True).first()
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
        paymentD.save()
        product_pay.quantity += 1
        product_pay.save()
        if paymentD.quantity == 0:
            paymentD.delete()
        return JsonResponse({'mensaje': 'Producto eliminado'}, status=200)
    except Product_payment.DoesNotExist:
        return JsonResponse({'error': 'Compra no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@api_view(['POST'])
def complete_payment(request):
    #Este metodo es para completar la compra y enviar la factura con los detalles
    try:
        payment = Product_payment.objects.filter(state=True).first()
        payment.state = False
        payment.save()
        product = payment.products.all()
        products_info = []
        discount_total = 0
        for p in product:
            product_pay = Product.objects.get(id=p.id)
            detailsP = ProductPaymentDetail.objects.filter(payment=payment, product=product_pay).first()
            discount_total += (product_pay.price * (product_pay.discount/100)) * detailsP.quantity
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
Descuento: ${discount_total}

Productos:
{products_details}

Ya puedes pasar a retirar tu compra en el establecimiento.

Gracias por preferirnos,
Nicelook"""

        remitente = settings.EMAIL_HOST_USER
        print(payment.client.user.email)
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
def filter_products(request, establisment_id):
    name = request.query_params.get("name")
    try: 
        establisment = Establisment.objects.get(id=establisment_id)
        products = Product.objects.filter(establisment=establisment, name__icontains=name)
            
        for p in products:
            if p.quantity == 0:
                p.save()
                p.delete()

        data = []
        for product in products:
            image = ImageProduct.objects.filter(id_product=product).first()
            if not image:
                image_product_url = None
            else:
                image_binaria = image.image
                image_base64 = base64.b64encode(image_binaria).decode('utf-8')
                mime_type = "image/jpeg"
                image_product_url = f"data:{mime_type};base64,{image_base64}"
            review = ReviewProduct.objects.filter(product=product)
            if not review:
                rating = 0
            else:
                contador = 0
                rating = 0
                for r in review:
                    contador += 1
                    rating += r.rating
                rating = rating/contador
            data.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "brand": product.brand,
                    "distributor": product.distributor,
                    "entry_date": product.entry_date,
                    "expiration_date": product.expiration_date,
                    "quantity": product.quantity,
                    "estate": product.estate,
                    "discount": product.discount,
                    "purchase_price": product.purchase_price,
                    "code": product.code,
                    "image": image_product_url,
                    "reviews": rating
                })

        return Response(
            {"products": data},
            status=status.HTTP_200_OK
            )
    except Exception as e:
        return Response(
            {"error": f"Error en el servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(["GET"])
def list_products(request, establisment_id):
    try: 
        establisment = Establisment.objects.get(id=establisment_id)
        products = Product.objects.filter(establisment=establisment)[:4]
            
        for p in products:
            if p.quantity == 0:
                p.save()

        data = []
        for product in products:
            image = ImageProduct.objects.filter(id_product=product).first()
            if not image:
                image_product_url = None
            else:
                image_binaria = image.image
                image_base64 = base64.b64encode(image_binaria).decode('utf-8')
                mime_type = "image/jpeg"
                image_product_url = f"data:{mime_type};base64,{image_base64}"
            review = ReviewProduct.objects.filter(product=product)
            contador = 0
            rating = 0
            if review:
                for r in review:
                    contador += 1
                    rating += r.rating
                rating = rating/contador
            if product.quantity > 0:
                data.append({
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "price": product.price,
                        "brand": product.brand,
                        "distributor": product.distributor,
                        "entry_date": product.entry_date,
                        "expiration_date": product.expiration_date,
                        "quantity": product.quantity,
                        "estate": product.estate,
                        "discount": product.discount,
                        "purchase_price": product.purchase_price,
                        "code": product.code,
                        "image": image_product_url,
                        "review": rating,
                        "establisment": product.establisment.id
                    })

        return Response(
            {"products": data},
            status=status.HTTP_200_OK
            )
    except Exception as e:
        return Response(
            {"error": f"Error en el servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(["DELETE"])
def delete_product(request, code):
    try:
        # Busca el producto dinámicamente con el ID proporcionado
        product = Product.objects.get(code=code)
        
        # Encuentra pagos asociados al producto
        payments = Product_payment.objects.filter(products=product, state=True)
        
        # Valida si hay detalles de pagos asociados
        details = ProductPaymentDetail.objects.filter(payment__in=payments, product=product).first()
        if not details:
            return Response({'message': 'No payment details found for this product'}, status=status.HTTP_404_NOT_FOUND)
        
        # Elimina el detalle encontrado
        product.quantity += details.quantity
        product.save()
        details.delete()
        
        return Response({'message': 'Producto eliminado'}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'message': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
