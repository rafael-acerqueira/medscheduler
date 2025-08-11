import pytest
import datetime
import random
from django.utils import timezone

from core.models import (
    User,
    Specialty,
    DoctorProfile,
    PatientProfile,
    Appointment,
)

def _unique_cpf():

    return f"{random.randint(10**10, 10**11 - 1)}"

def _unique_crm():

    return f"CRM{random.randint(10000, 99999)}"


@pytest.fixture
def specialty(db):
    return Specialty.objects.create(name="Cardiology")


@pytest.fixture
def user_doctor(db):
    user = User.objects.create_user(
        username="doctor1",
        password="testpass123",
        role=User.DOCTOR,
        is_active=True,
    )

    DoctorProfile.objects.create(user=user, crm=_unique_crm())
    return user


@pytest.fixture
def doctor_profile(db, user_doctor, specialty):

    profile, _ = DoctorProfile.objects.get_or_create(user=user_doctor, defaults={"crm": _unique_crm()})
    profile.specialties.add(specialty)
    return profile


@pytest.fixture
def user_patient(db):
    user = User.objects.create_user(
        username="patient1",
        password="testpass123",
        role=User.PATIENT,
        is_active=True,
    )

    PatientProfile.objects.create(user=user, cpf=_unique_cpf())
    return user


@pytest.fixture
def appointment(db, user_patient, user_doctor, specialty):
    return Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=2),
        time=datetime.time(10, 0),
        reason="Rotina",
        status="confirmed",
    )
