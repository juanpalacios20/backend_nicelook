#aqui va toda la magia, bienvenidos a disneyland
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from administrator.models import Administrator
from product.models import Product
from establisment.models import Establisment
from django.middleware.csrf import get_token
from product.serializers import productSerializer
from Image_product.models import ImageProduct
import base64
from django.http import JsonResponse


@api_view(['POST'])
def register(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=email,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    
    Administrator.objects.create(user=user)

    user.save()
    token = Token.objects.create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def loginAdmin(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email=email).first()
    
    if not user or not user.check_password(password):
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = Token.objects.filter(user=user).first()
    if not token:
        token = Token.objects.create(user=user)
        
    csrf_token = get_token(request)
    
    return Response({'token': token.key, 'csrf_token': csrf_token}, status=status.HTTP_200_OK)

@api_view(['POST'])
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
        estate = True
        
        if not name or not description or not price or not distributor or not entry_date or not expiration_date or not quantity or not establisment:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        Product.objects.create(name=name,
                               description=description, 
                               price=price, distributor=distributor, 
                               entry_date=entry_date, expiration_date=expiration_date, 
                               quantity=quantity, estate=estate,
                               establisment=Establisment.objects.get(id=establisment),
                               brand=brand, discount=0)
        return Response({'message': 'Product added successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getProducts(request):
    try:
        products = Product.objects.all()
        serializer = productSerializer(products, many=True)
        return Response({'products': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
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
        
        product = Product.objects.get(id=product_id)
        
        if name:
            product.name = name
        if description:
            product.description = description
        if price:
            product.price = price
        if brand:
            product.brand = brand
        if distributor:
            product.distributor = distributor
        if entry_date:
            product.entry_date = entry_date
        if expiration_date:
            product.expiration_date = expiration_date
        if quantity:
            product.quantity = quantity
        if estate:
            product.estate = estate
        if discount:
            product.discount = discount
        product.save()
        return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
    
@api_view(['DELETE'])
def deleteProduct(request):
    try:
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def uploadImage(request):
    try:
        id_establisment = request.data.get('id_establisment')
        id_product = request.data.get('id_product')
        image = request.FILES.get('image')
        imageField = image.read()

        ImageProduct.objects.create(id_establisment=Establisment.objects.get(id=id_establisment),
                                    id_product=Product.objects.get(id=id_product),
                                    image=imageField)
        return Response({'message': 'Image uploaded successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getImageProduct(request):
    try:
        id_product = request.data.get('id_product')
        id_establisment = request.data.get('id_establisment')
        imagesList = []

        image = ImageProduct.objects.filter(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product))
        for image in image:
            imageBase64 = base64.b64encode(image.image).decode('utf-8')
            mime_type = "image/jpeg"
            image_base64_url = f"data:{mime_type};base64,{imageBase64}"
            imagesList.append({"imagen": image_base64_url})
        
        return JsonResponse({'imagenes': imagesList})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def updateImageProduct(request):
    try:
        id_establisment = request.data.get('id_establisment')
        id_product = request.data.get('id_product')
        id_image = request.data.get('id_image')
        image = request.FILES.get('image')
        imageField = image.read()

        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product), id=id_image)
        imageProduct.image = imageField
        imageProduct.save()
        return Response({'message': 'Image updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteImageProduct(request):
    try:
        id_establisment = request.data.get('id_establisment')
        id_product = request.data.get('id_product')
        id_image = request.data.get('id_image')
        imageProduct = ImageProduct.objects.get(id_establisment=Establisment.objects.get(id=id_establisment), id_product=Product.objects.get(id=id_product), id=id_image)
        imageProduct.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    





        
        
    


