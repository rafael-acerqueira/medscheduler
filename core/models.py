from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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

    def is_patient(self):
        return self.role == self.PATIENT

    def is_doctor(self):
        return self.role == self.DOCTOR

    def is_admin(self):
        return self.role == self.ADMIN

    def has_completed_profile(self):
        if self.is_patient():
            try:
                profile = self.patientprofile
                return all([profile.cpf, profile.birthdate])
            except PatientProfile.DoesNotExist:
                return False
        elif self.is_doctor():
            try:
                profile = self.doctorprofile
                return all([profile.crm, profile.specialty])
            except DoctorProfile.DoesNotExist:
                return False
        return True


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True)
    birthdate = models.DateField(null=True, blank=True)
    health_plan = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crm = models.CharField(max_length=20, unique=True)
    specialty = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Doctor: {self.user.get_full_name()}"

