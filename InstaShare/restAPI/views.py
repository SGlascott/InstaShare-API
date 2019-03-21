from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from restAPI import models, Serializers

from .Tools.aws import CollectionTools, RekognitionTools
from .Tools.DevOps import credentials

# Returns list of users if staff otherwise it returns the user who calls it
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

#Create new User
class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = Serializers.UserSerializer


#old, may not need anymore
class UserDetail(generics.RetrieveAPIView):
    queryset = models.UserExtension.objects.all()
    serializer_class = Serializers.UserSerializer

#new contact view
class ContactView(APIView):
    def post(self, request, format=None):
        contact_photo = Serializers.ContactsObjectSerializer(data = request.data)
        if contact_photo.is_valid():
            user_ext = models.UserExtension.objects.get(user=request.user)
            #dont know if its saving photo
            contact_photo = contact_photo.save()
            face_id = CollectionTools.adding_faces_to_a_collection(request.user.id, user_ext.contacts_collection_id, contact_photo.photo)
            print('Face ID: ', face_id)
            serializer = Serializers.ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user = request.user, face_id=face_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(contact_photo.errors, status=status.HTTP_400_BAD_REQUEST)

class RekognitionView(APIView):
    def post(self, request, format=None):
        group_photo = Serializers.RekognitionSerializer(data = request.data)
        if group_photo.is_valid():
            group_photo = group_photo.save()
            print(request.user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
