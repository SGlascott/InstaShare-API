from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status
from . import models
from . import views
import json, base64
from .Tools.aws import CollectionTools
from rest_framework.test import APIClient, force_authenticate
import logging

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
        
    def test_upload_contact(self):
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(self.url, self.ContactPayloadScott, format='json')
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.delete = CollectionTools.deleting_a_Collection(self.collection_id)
        self.assertTrue(self.delete)

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
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(self.url, self.ContactPayloadScott, format='json')
        self.response = client.post(self.url, self.ContactPayloadAnanth, format='json')
        self.response = client.post(self.url, self.ContactPayloadTalat, format='json')
        with open("restAPI/TestImages/GroupPhotos/2.jpg", "rb") as image_file:
            self.groupPhoto = base64.b64encode(image_file.read())
        self.payload = {
            'base_64': self.groupPhoto
        }
    def test_single_photo(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(reverse('restAPI:singlePhoto'), self.payload,  format='json')
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
        self.delete = CollectionTools.deleting_a_Collection(self.collection_id)
        self.assertTrue(self.delete)

class batchUploadTest(TestCase):
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
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(self.url, self.ContactPayloadScott, format='json')
        self.response = client.post(self.url, self.ContactPayloadAnanth, format='json')
        self.response = client.post(self.url, self.ContactPayloadTalat, format='json')
        with open("restAPI/TestImages/GroupPhotos/1.jpg", "rb") as image_file:
            self.groupPhoto1 = base64.b64encode(image_file.read())
        with open("restAPI/TestImages/GroupPhotos/2.jpg", "rb") as image_file:
            self.groupPhoto2 = base64.b64encode(image_file.read())
        with open("restAPI/TestImages/GroupPhotos/3.jpg", "rb") as image_file:
            self.groupPhoto3 = base64.b64encode(image_file.read())
        
        self.payload = [
            {'base_64': self.groupPhoto2},
            {'base_64': self.groupPhoto1},
            {'base_64': self.groupPhoto3},
        ]
    def test_batch_upload(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(reverse('restAPI:batchUpload'), self.payload,  format='json')
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
        self.delete = CollectionTools.deleting_a_Collection(self.collection_id)
        self.assertTrue(self.delete)

class batchUploadAndroidTest(TestCase):
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
        self.token = self.client.post(reverse('restAPI:token'), {'username': 'UnitTestAcc', 'password': 'McTest1'}).data.pop('access')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(self.url, self.ContactPayloadScott, format='json')
        self.response = client.post(self.url, self.ContactPayloadAnanth, format='json')
        self.response = client.post(self.url, self.ContactPayloadTalat, format='json')
        with open("restAPI/TestImages/GroupPhotos/1.jpg", "rb") as image_file:
            self.groupPhoto1 = base64.b64encode(image_file.read())
        with open("restAPI/TestImages/GroupPhotos/2.jpg", "rb") as image_file:
            self.groupPhoto2 = base64.b64encode(image_file.read())
        with open("restAPI/TestImages/GroupPhotos/3.jpg", "rb") as image_file:
            self.groupPhoto3 = base64.b64encode(image_file.read())
        
        self.payload = [
            {'base_64': self.groupPhoto2},
            {'base_64': self.groupPhoto1},
            {'base_64': self.groupPhoto3},
        ]
    def test_batch_upload(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response = client.post(reverse('restAPI:batchAndroid'), self.payload,  format='json')
        print(self.response.data)
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
        self.delete = CollectionTools.deleting_a_Collection(self.collection_id)
        self.assertTrue(self.delete)