from django.contrib.auth.models import User
from rest_framework import serializers
from restAPI import models
from .Tools.aws import CollectionTools

from django.core.files import File
import base64

from PIL import Image

import datetime
class UserSerializer(serializers.ModelSerializer):
    """Serializer used for parsing our User JSON Data
    
    The serializer utilizes two models: BaseUser, UserExtension. First, the serializer established what fields
    are part of the User model. Then the Meta Class defines the expected fields for the JSON data. Finally, we define a create
    method to define the creation of the new User Objects and Models.
    """
    username = serializers.CharField(source='user.username')
    password = serializers.CharField(style={'input_type': 'password'}, source='user.password')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.CharField()

    class Meta:
        model = models.UserExtension
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'phone_number')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            **user_data
        )
        user.is_staff = False

        collection_id = CollectionTools.creating_a_collection(user.id)

        userExention = models.UserExtension.objects.create(user=user, contacts_collection_id=collection_id, **validated_data)

        return userExention

#Serializer for contact view
class ContactSerializer(serializers.ModelSerializer):  
    class Meta:
        model = models.Contact
        fields = ('id', 'name', 'phone_number')
        read_only_fields = ('id',)

    def create(self, validated_data):
        #upload to AWS and save collectionID here:
        contact = models.Contact.objects.create(**validated_data)

        return contact

#Second serializer for contact upload, used for seperating the contact photo from the data.
class ContactsObjectSerializer(serializers.Serializer):
    contact_photo = serializers.ImageField()    
    class Meta:
        fields = ('contact_photo', )
    
    def create(self, validated_data):
        return ContactsObjectSerializer.contactObj(validated_data.pop('contact_photo'))
    
    class contactObj(object):
        def __init__(self, photo):
            self.photo = photo

class RekognitionListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        print(validated_data)
        photos = []
        for item in validated_data:
            print(item)
        return photos

class RekognitionSerializer(serializers.Serializer):
    group_photo = serializers.ImageField()
    class Meta:
        list_serializer_class = RekognitionListSerializer
        fields = ('group_photo',)
    
    class rekognitionImage(object):
        def __init__(self, photo):
            self.photo = photo
    
    def create(self, validated_data):
        print('single called')
        return RekognitionSerializer.rekognitionImage(validated_data.pop('group_photo'))

class ContactRekognitionSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    name=serializers.CharField()
    phone_number=serializers.CharField()
    class Meta:
        fields = ('id', 'name', 'phone_number')

class ImageBase64(serializers.Serializer):
    base_64 = serializers.CharField()
    class Meta:
        fields = ('base_64',)

    def create(self, validated_data):
        image_data = base64.b64decode(validated_data.pop('base_64'))
        return image_data

class BatchSerializerNew(serializers.Serializer):
    group_photo = serializers.CharField()
    class Meta:
        fields = ('group_photo',)

    def create(self, validated_data):
        image_data = base64.b64decode(validated_data.pop('group_photo'))
        return image_data

class BatchListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        print(validated_data)
        photos = []
        for item in validated_data:
            print(item)
        return photos

class BatchSerializer(serializers.Serializer):
    TemporaryUploadedFile = serializers.ImageField()
    class Meta:
        list_serializer_class = BatchListSerializer
        fields = ('TemporaryUploadedFile',) 
    
class errorMsgSerializer(serializers.Serializer):
    msg = serializers.CharField()
    class Meta:
        fields = ('msg')

class AndroidBatchSerializer(serializers.Serializer):
    contacts = ContactSerializer(many = True, read_only=True)
    urls = serializers.ListField()

    class Meta:
        fields = ('contacts', 'urls')