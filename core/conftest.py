import pytest
from core.models import User, Specialty, DoctorProfile, Appointment
import datetime
import random
from django.utils import timezone

@pytest.fixture
def specialty(db):
    return Specialty.objects.create(name="Cardiology")

@pytest.fixture
def user_doctor(db):
    user = User.objects.create_user(
        username="doctor1",
        password="testpass123",
        role=User.DOCTOR,
        is_active=True
    )
    return user

@pytest.fixture
def doctor_profile(db, user_doctor, specialty):
    profile = DoctorProfile.objects.get(user=user_doctor)
    profile.specialties.add(specialty)
    return profile

@pytest.fixture
def user_patient(db):
    user = User.objects.create_user(
        username="patient1",
        password="testpass123",
        role=User.PATIENT,
        is_active=True
    )
    user.patientprofile.cpf = f"{random.randint(10000000000, 99999999999)}"
    user.patientprofile.save()
    return user

@pytest.fixture
def appointment(user_patient, user_doctor, specialty):
    appointment = Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=2),
        time=datetime.time(10, 0),
        reason="Rotina",
        status="confirmed"
    )
    return appointment


