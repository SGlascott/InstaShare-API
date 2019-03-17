from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from restAPI import models, Serializers


# Create your views here.
class UserList(APIView):
    def get(self, request, format=None):
        if request.user.is_staff:
            user = models.UserExtension.objects.all()
            serializer = Serializers.UserSerializer(user, many=True)
            return Response(serializer.data)
        else:
            user = models.UserExtension.objects.get(user=request.user)
            serializer = Serializers.UserSerializer(user)
            return Response(serializer.data)

class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = Serializers.UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = models.UserExtension.objects.all()
    serializer_class = Serializers.UserSerializer


class ContactView(APIView):
    def post(self, request, format=None):
        serializer = Serializers.ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)