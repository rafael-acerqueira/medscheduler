import pytest
from core.models import User, Specialty, DoctorProfile

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
    return User.objects.create_user(
        username="patient1",
        password="testpass123",
        role=User.PATIENT,
        is_active=True
    )
