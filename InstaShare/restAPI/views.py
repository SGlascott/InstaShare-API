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
import base64

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
            face_id = CollectionTools.adding_faces_to_a_collection(request.user.id, user_ext.contacts_collection_id, contact_photo.photo, True)
            print('Face ID: ', face_id)
            serializer = Serializers.ContactSerializer(data=request.data)
            if serializer.is_valid() and face_id != -1:
                serializer.save(user = request.user, face_id=str(face_id[0]))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(contact_photo.errors, status=status.HTTP_400_BAD_REQUEST)


#contact view for mobile use.
class ContactViewMobile(APIView):
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
            face_id = CollectionTools.adding_faces_to_a_collection(request.user.id, user_ext.contacts_collection_id, contact_photo, True)
            print('Face ID: ', face_id)
            serializer = Serializers.ContactSerializer(data=request.data)
            if serializer.is_valid() and face_id != -1:
                serializer.save(user = request.user, face_id=str(face_id[0]))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(contact_photo.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        try:
            contact = models.Contact.objects.get(id=id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        contactSerializer = Serializers.ContactSerializer(contact, data=request.data)
        if contactSerializer.is_valid():
            contactSerializer.save()
            return Response(contactSerializer.data, status=status.HTTP_200_OK)
        return Response(contactSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


#single photo rekognition
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

#single photo rekognition for mobile
class RekognitionViewMobile(APIView):
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

#upload multiple photos for rekognition. Primarily used for testing logic before mobile dev.
class BatchUploadView(APIView):
    def post(self, request, format=None):
        try:
            photos = []
            for i in request.data.pop('group_photo'):
                photos.append(i)
            user_id = request.user.id
            collection_id = models.UserExtension.objects.get(user=request.user).contacts_collection_id
            list_of_added_face_ids = []
            for photo in photos:
                added_face_ids = CollectionTools.adding_faces_to_a_collection(request.user.id, collection_id, photo)
                list_of_added_face_ids = list_of_added_face_ids + added_face_ids

            all_contacts = list(models.Contact.objects.filter(user=request.user))
            new_contacts_face_ids = []
            for contact in all_contacts:
                new_contacts_face_ids.append(contact.face_id)

            matched_contacts = RekognitionTools.search_faces_by_contact(collection_id, list_of_added_face_ids, new_contacts_face_ids)

            contacts = models.Contact.objects.filter(face_id__in=matched_contacts)
            
            contact_serializer = Serializers.ContactRekognitionSerializer(contacts, many=True)
            return Response(contact_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

#upload multiple photos for mobile
class BatchUploadViewMobile(APIView):
    def post(self, request, format=None):
        #convert photos from base 64 to jpg and save in photos array
        try:
            photos = []
            for i in request.data.pop('group_photo'):
                photos.append(base64.b64decode(i)) 
        except:
            return Response(Serializers.errorMsgSerializer({'msg':'Photo Error'}).data,status=status.HTTP_400_BAD_REQUEST)

        #get the user info
        user_id = request.user.id
        collection_id = models.UserExtension.objects.get(user=request.user).contacts_collection_id
        removed_doups = []

        #run rekognition
        try:
            for photo in photos:
                photo_faces = RekognitionTools.search_faces_by_image(user_id, photo, collection_id)

                for face in photo_faces:
                    if face not in removed_doups:
                        removed_doups.append(face)
        except:
            return Response(Serializers.errorMsgSerializer({'msg':'AWS Error'}).data, status=status.HTTP_400_BAD_REQUEST)
        
        #Return info to users
        try:
            contacts = models.Contact.objects.filter(face_id__in=removed_doups)
            print(contacts)
            contact_serializer = Serializers.ContactRekognitionSerializer(contacts, many=True)
            return Response(contact_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(contact_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


