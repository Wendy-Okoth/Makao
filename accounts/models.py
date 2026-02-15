
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_landlord = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()

    def __str__(self):
        return f"{self.username} ({'Landlord' if self.is_landlord else 'Tenant'})"
