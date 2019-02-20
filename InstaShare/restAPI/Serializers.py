from django.contrib.auth.models import User
from rest_framework import serializers
from restAPI import models

class UserSerializer(serializers.ModelSerializer):
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
   #username = validated_data.pop('username')
        #password = validated_data.pop('password')
        #email = validated_data.pop('email')
        #first_name = validated_data.pop('first_name')
        #last_name = validated_data.pop('last_name')

        user = User.objects.create(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name')
        )
        user.is_staff = False
        user.set_password(validated_data.pop('password'))
        user.save()
        userExention = models.UserExtension.objects.create(user=user, **validated_data)

        return userExention