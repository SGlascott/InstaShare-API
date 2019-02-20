from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=11)

    def __str__(self):
        return str(self.user.get_full_name())