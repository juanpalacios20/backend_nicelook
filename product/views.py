from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import productSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status
from establisment.models import Establisment
# Create your views here.
class productoViewSet(viewsets.ModelViewSet):
    serializer_class = productSerializer
    queryset =Product.objects.all()


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def addProduct(request):
    try:
        name = request.data.get('name')
        establisment = request.data.get('establisment')
        description = request.data.get('description')
        price = request.data.get('price')
        distributor = request.data.get('distributor')
        entry_date = request.data.get('entry_date')
        expiration_date = request.data.get('expiration_date')
        quantity = request.data.get('quantity')
        brand = request.data.get('brand')
        code = request.data.get('code')
        purchase_price = request.data.get('purchase_price')
        estate = True

        if not name or not price or not distributor or not entry_date or not expiration_date or not quantity or not establisment:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not description:
            description = ''
        if Product.objects.filter(code=code).exists():
            return Response({'error': 'codigo ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not description:
            description = ''
        
        Product.objects.create(name=name,code=code,
                               description=description, 
                               price=price, distributor=distributor, 
                               entry_date=entry_date, expiration_date=expiration_date, 
                               quantity=quantity, estate=estate,
                               establisment=Establisment.objects.get(id=establisment),
                               brand=brand, discount=0, purchase_price=purchase_price)
        return Response({'message': 'Product added successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getProducts(request):
    try:
        id_establisment = request.query_params.get('id_establisment')
        if not id_establisment:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        products = Product.objects.filter(establisment=Establisment.objects.get(id=id_establisment))
        serializer = productSerializer(products, many=True)
        return Response({'products': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
#@permission_classes([IsAuthenticated])
def updateProduct(request):
    try:
        product_id = request.data.get('product_id')
        name = request.data.get('name')
        description = request.data.get('description')
        price = request.data.get('price')
        brand = request.data.get('brand')
        distributor = request.data.get('distributor')
        entry_date = request.data.get('entry_date')
        expiration_date = request.data.get('expiration_date')
        quantity = request.data.get('quantity')
        estate = request.data.get('estate')
        discount = request.data.get('discount')
        code = request.data.get('code')
        purchase_price = request.data.get('purchase_price')
        
        product = Product.objects.get(id=product_id)
        
        
        if name:
            product.name = name
        if description:
            product.description = description
        if price and price > 0:
            product.price = price
        else:
            return Response({'error': 'Precio debe ser mayor a 0'}, status=status.HTTP_400_BAD_REQUEST)
        if brand:
            product.brand = brand
        if distributor:
            product.distributor = distributor
        if entry_date:
            product.entry_date = entry_date
        if expiration_date:
            product.expiration_date = expiration_date
        if quantity and quantity > 0:
            product.quantity = quantity
        else:
            return Response({'error': 'Qantidad debe ser mayor a 0'}, status=status.HTTP_400_BAD_REQUEST)    
        if not estate:
            product.estate = estate
        else:
            product.estate = True
        if code and code > 0 and not Product.objects.filter(code=code).exists():
            product.code = code
        else:
            return Response({'error': 'Code debe ser mayor a 0 y no debe existir'}, status=status.HTTP_400_BAD_REQUEST)
        if discount:
            product.discount = discount
        if purchase_price and purchase_price > 0:
            product.purchase_price = purchase_price
        else:
            return Response({'error': 'Precio de compra debe ser mayor a 0'}, status=status.HTTP_400_BAD_REQUEST)
        product.save()
        return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
    
@api_view(['DELETE'])
#@permission_classes([IsAuthenticated])
def deleteProduct(request):
    try:
        product_id = request.query_params.get('product_id')
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def alert(request, id_establisment):
    try:
        # Obtener los productos del establecimiento
        products = Product.objects.filter(establisment=Establisment.objects.get(id=id_establisment)) 
        
        # Lista para almacenar los productos con menos de 5 unidades
        low_stock_products = []

        # Revisar cada producto
        for p in products:
            if p.quantity <= 5:
                low_stock_products.append(p.name)

        # Verificar si hay productos con baja cantidad
        if low_stock_products:
            return Response({
                'message': 'El producto/los productos ' + ', '.join(low_stock_products) + ' están propensos a agotar existencias (tienen menos de 5 unidades)'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No hay productos con menos de 5 unidades'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
