from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status
from . import models
from . import views
import json, base64
from .Tools.aws import CollectionTools

# Create your tests here.
class registerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory
        self.payload = {
            'username': 'UnitTestAcc',
            'password': 'UnitTest123',
            'email': 'test@unit.com',
            'first_name': 'Unit',
            'last_name': 'McTest',
            'phone_number': '1234567899',
            }
        self.url = reverse('restAPI:register')
        self.view = views.CreateUserView.as_view()
    
    def test_register_user(self):
        self.response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.user = models.User.objects.get(id = self.response.data.pop('id'))
        self.userExt = models.UserExtension.objects.get(user= self.user)

class getTestUserTest(TestCase):
    def setUp(self):
        self.user = models.User.objects.create_user('UnitTestAcc', email='unit@test.com', password='McTest1')

    def test_get_user(self):
        self.assertEqual(self.user.username, 'UnitTestAcc')

class uploadContactsTest(TestCase):
    def setUp(self):
        self.url = reverse('restAPI:uploadContact')
        self.user = models.User.objects.create_user('UnitTestAcc', email='unit@test.com', password='McTest1')
        self.collection_id = CollectionTools.creating_a_collection(self.user.id)
        self.userExtension = models.UserExtension.objects.create(user = self.user, phone_number='1234567890', contacts_collection_id=self.collection_id)
        with open("restAPI/TestImages/Contacts/Scott.jpg", "rb") as image_file:
            self.contactPhotoScott = base64.b64encode(image_file.read())
        self.ContactPayloadScott = {
            'name': 'Scott G',
            'phone_number': '1236541234',
            'base_64': self.contactPhotoScott
        }
        with open("restAPI/TestImages/Contacts/Ananth.jpg", "rb") as image_file:
            self.contactPhotoAnanth = base64.b64encode(image_file.read())
        self.ContactPayloadAnanth = {
            'name': 'Ananth',
            'phone_number': '1236541233',
            'base_64': self.contactPhotoAnanth
        }
        with open("restAPI/TestImages/Contacts/Talat.jpg", "rb") as image_file:
            self.contactPhotoTalat = base64.b64encode(image_file.read())
        self.ContactPayloadTalat = {
            'name': 'Talat R',
            'phone_number': '1236541231',
            'base_64': self.contactPhotoTalat
        }


    def test_upload_contact(self):
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        self.headers={
            'Authorization': "Bearer " + self.token
        }
        self.response = self.client.post(self.url, self.ContactPayloadScott, format='json')
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

class singlePhotoTest(TestCase):
    def setUp(self):
        self.url = reverse('restAPI:uploadContact')
        self.user = models.User.objects.create_user('UnitTestAcc', email='unit@test.com', password='McTest1')
        self.collection_id = CollectionTools.creating_a_collection(self.user.id)
        self.userExtension = models.UserExtension.objects.create(user = self.user, phone_number='1234567890', contacts_collection_id=self.collection_id)
        with open("restAPI/TestImages/Contacts/Scott.jpg", "rb") as image_file:
            self.contactPhotoScott = base64.b64encode(image_file.read())
        self.ContactPayloadScott = {
            'name': 'Scott G',
            'phone_number': '1236541234',
            'base_64': self.contactPhotoScott
        }
        with open("restAPI/TestImages/Contacts/Ananth.jpg", "rb") as image_file:
            self.contactPhotoAnanth = base64.b64encode(image_file.read())
        self.ContactPayloadAnanth = {
            'name': 'Ananth',
            'phone_number': '1236541233',
            'base_64': self.contactPhotoAnanth
        }
        with open("restAPI/TestImages/Contacts/Talat.jpg", "rb") as image_file:
            self.contactPhotoTalat = base64.b64encode(image_file.read())
        self.ContactPayloadTalat = {
            'name': 'Talat R',
            'phone_number': '1236541231',
            'base_64': self.contactPhotoTalat
        }
        self.response = self.client.post(self.url, self.ContactPayloadScott, format='json')
        self.response = self.client.post(self.url, self.ContactPayloadAnanth, format='json')
        self.response = self.client.post(self.url, self.ContactPayloadTalat, format='json')
        with open("restAPI/TestImages/GroupPhotos/2.jpg", "rb") as image_file:
            self.groupPhoto = base64.b64encode(image_file.read())
        self.payload = {
            'base_64':self.groupPhoto
        }
    def test_single_photo(self):
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        self.headers={
            'Authorization': "Bearer " + self.token
        }
        self.response = self.client.post(reverse('restAPI:singlePhoto'), self.payload, headers=self.headers, format='json')
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
