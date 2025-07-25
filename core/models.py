from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone

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

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        if Specialty.objects.exclude(pk=self.pk).filter(name__iexact=self.name.strip()).exists():
            raise ValidationError("A specialty with this name already exists.")
        self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

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
    phone = models.CharField(max_length=20, blank=True)

    specialties = models.ManyToManyField(Specialty, related_name='doctors', blank=True)

    def __str__(self):
        return f"Doctor: {self.user.get_full_name()}"




class Appointment(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient',
        limit_choices_to={'role': 'patient'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_doctor',
        limit_choices_to={'role': 'doctor'}
    )
    specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='confirmed')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'time')
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"

    @property
    def can_be_cancelled(self):
        return self.status == "confirmed" and (self.date > timezone.now().date() or (self.date == timezone.now().date() and self.time > timezone.now().time()))
