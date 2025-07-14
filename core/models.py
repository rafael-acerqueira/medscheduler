from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    PATIENT = 'patient'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (DOCTOR, 'Doctor'),
        (PATIENT, 'Patient'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=PATIENT,
        help_text='Role of the user: admin, doctor or patient'
    )


