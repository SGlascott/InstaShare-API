from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from restAPI import models, Serializers
from django.core.exceptions import ObjectDoesNotExist

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

class ContactView64(APIView):
    def get(self, request, format=None):
        try:
            contacts = models.Contact.objects.get(user=request.user)
            cSerializer = Serializers.ContactSerializer(contacts, many=True)
            return Response(cSerializer, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

    def post(self, request, format=None):
        contact_photo = Serializers.ImageBase64(data = request.data)
        if contact_photo.is_valid():
            user_ext = models.UserExtension.objects.get(user=request.user)
            #dont know if its saving photo
            contact_photo = contact_photo.save()
            face_id = CollectionTools.adding_faces_to_a_collection(request.user.id, user_ext.contacts_collection_id, contact_photo)
            print('Face ID: ', face_id)
            serializer = Serializers.ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user = request.user, face_id=face_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(contact_photo.errors, status=status.HTTP_400_BAD_REQUEST)

        def put(self, request, format=None, id):
            try:
                contact = models.Contact.objects.get(id=id)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            contactSerializer = Serializers.ContactSerializer(contact, data=request.data)
            if contactSerializer.is_valid():
                contactSerializer.save()
                return Response(contactSerializer.data, status=status.HTTP_200_OK)
            return Response(contactSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RekognitionView(APIView):
    def post(self, request, format=None):
        group_photo = Serializers.RekognitionSerializer(data = request.data)
        if group_photo.is_valid():
            group_photo = group_photo.save()
            user_id = request.user.id
            #print('userId: ', user_id)
            collection_id = models.UserExtension.objects.get(user=request.user).contacts_collection_id
            #print('col: ', collection_id)
            face_ids = RekognitionTools.search_faces_by_image(user_id, group_photo.photo, collection_id)
            print(len(face_ids))
            contacts = []
            for i in face_ids:
                try:
                    contacts.append(models.Contact.objects.get(face_id=i))
                    print(i, 'found')
                except ObjectDoesNotExist:
                    pass
            if contacts == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                contact_serializer = Serializers.ContactRekognitionSerializer(contacts, many=True)
                return Response(contact_serializer.data, status=status.HTTP_200_OK)
            #if contact_serializer.is_valid():
                #return Response(contact_serializer.data, status=status.HTTP_200_OK)
            #else:
                #return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RekognitionViewB64(APIView):
    def post(self, request, format=None):
        group_photo_serializer = Serializers.ImageBase64(data = request.data)
        if group_photo_serializer.is_valid():
            #print(group_photo_serializer)
            group_photo_serializer = group_photo_serializer.save()
            user_id = request.user.id
            #print('photo: ', group_photo_serializer)
            collection_id = models.UserExtension.objects.get(user=request.user).contacts_collection_id
            #print('col: ', collection_id)
            face_ids = RekognitionTools.search_faces_by_image(user_id, group_photo_serializer, collection_id)
            print(len(face_ids))
            contacts = []
            for i in face_ids:
                try:
                    contacts.append(models.Contact.objects.get(face_id=i))
                    #print(contacts[-1])
                except ObjectDoesNotExist:
                    pass
            if contacts == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                contact_serializer = Serializers.ContactRekognitionSerializer(contacts, many=True)
                return Response(contact_serializer.data, status=status.HTTP_200_OK)
            #else:
             #   return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

#currently O(n^2) but we should be able to optimize to O(n)
class BatchUploadView(APIView):
    def post(self, request, format=None):
        try:
            photos = []
            for i in request.data.pop('group_photo'):
                photos.append(i) 
            user_id = request.user.id
            collection_id = models.UserExtension.objects.get(user=request.user).contacts_collection_id
            removed_doups = []
            for photo in photos:
                photo_faces = RekognitionTools.search_faces_by_image(user_id, photo, collection_id)

                for face in photo_faces:
                    if face not in removed_doups:
                        removed_doups.append(face)
            
            contacts = models.Contact.objects.filter(face_id__in=removed_doups)
            print(contacts)
            contact_serializer = Serializers.ContactRekognitionSerializer(contacts, many=True)
            return Response(contact_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


