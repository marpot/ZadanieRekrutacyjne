from rest_framework import serializers

from django.contrib.auth import get_user_model
from collections import namedtuple

UserModel = get_user_model()

#class UploadedImageSerializer(serializers.ModelSerializer):
 #   class Meta:
   ##     model = UploadedImage
     #   fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only = True)
    
    def create(self, validated_data):
        
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        
        return user
    
    class Meta:
        model = UserModel
        fields = ("id", "username", "password")

class ImageSerializer(serializers.ModelSerializer):
    thumbnail_200px = serializers.ImageField(read_only=True)
    thumbnail_400px = serializers.ImageField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class ImageTier: namedtuple('ImageTier', ['name', 'thumbnail_size_200', 'thumbnail_size_400', 'image_link_expiration'])

    BUILTIN_TIERS = {
    'basic': ImageTier('Basic', 200, None, None),
    'premium': ImageTier('Premium', 200, 400, None),
    'enterprise': ImageTier('Enterprise', 200, 400, (300, 30000)),
    }      

    class ImageSerializer(serializers.ModelSerializer):
        thumbnail_200px = serializers.ImageField(read_only=True)
        thumbnail_400px = serializers.ImageField(read_only=True)
        image = serializers.ImageField(read_only=True)
    class Meta:
           model = Image
           fields = ('id', 'image', 'thumbnail_200px', 'thumbnail_400px')

    def create(self, validated_data):
       image = validated_data['image']
       user = validated_data['user']
       tier = user.account_tier
       thumbnail_size_200 = tier.thumbnail_size_200
       thumbnail_size_400 = tier.thumbnail_size_400
       image_link_expiration = tier.image_link_expiration
       image_obj = Image.objects.create(user=user, image=image)
       image_obj.create_thumbnails(thumbnail_size_200, thumbnail_size_400)
       if image_link_expiration:
           image_obj.create_expiring_link(*image_link_expiration)
       return image_obj

