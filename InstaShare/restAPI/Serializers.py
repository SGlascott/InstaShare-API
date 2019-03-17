from django.contrib.auth.models import User
from rest_framework import serializers
from restAPI import models

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

    class Meta:
        model = models.UserExtension
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'phoneNumber')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            **user_data
        )
        user.is_staff = False
        userExention = models.UserExtension.objects.create(user=user, **validated_data)

        return userExention

class ContactSerializer(serializers.ModelSerializer):
    #contact_photo = serializers.ImageField()

    class meta:
        model = models.Contact
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'contact_photo')
        read_only_fields = ('id')

    def create(self, validated_data):
        #photo = validated_data.pop('contact_photo')
        #upload to AWS and save collectionID here:
        collection_id = 'TEST COL ID'
        print('Type: ', type(validated_data) )
        print(validated_data)
        contact = models.Contact.objects.create(user=request.user, collection_id=collection_id, **validated_data)


