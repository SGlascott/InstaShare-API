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
        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            **user_data
        )
        user.is_staff = False
        userExention = models.UserExtension.objects.create(user=user, **validated_data)

        return userExention