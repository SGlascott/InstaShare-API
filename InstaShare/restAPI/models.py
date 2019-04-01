from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11)
    contacts_collection_id = models.CharField(max_length=50, null=True)

    def __str__(self):
        return str(self.user.get_full_name())

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    face_id = models.CharField(max_length=50, null=True)

    def __str__(self):
        return str(self.user.id) + ': ' +str(self.id)