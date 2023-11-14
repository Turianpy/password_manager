from api.utils import generate_salt
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    salt = models.BinaryField(null=True)

    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = generate_salt()
        super().save(*args, **kwargs)
