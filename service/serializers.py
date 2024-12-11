import base64
from rest_framework import serializers
from .models import Service
class serviceSerializer (serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ('id', 'name', 'price', 'commission', 'category', 'establisment', 'state', 'image_base64')

    def get_image_base64(self, obj):
        image = obj.image
        if not image:
            return None
        image_base64 = base64.b64encode(image).decode('utf-8')
        mime_type = "image/jpeg"
        image_base64_url = f"data:{mime_type};base64,{image_base64}"
        return image_base64_url