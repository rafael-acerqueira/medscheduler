from django.utils import timezone
import datetime

import pytest
from core.models import User, Specialty, Appointment, AppointmentFeedback

@pytest.mark.django_db
def test_create_specialty():
    spec = Specialty.objects.create(name="Cardiology")
    assert spec.pk is not None
    assert str(spec) == "Cardiology"


@pytest.mark.django_db
def test_create_patient_user():
    user = User.objects.create_user(
        username="patient1",
        email="patient1@email.com",
        password="testpass123",
        role=User.PATIENT,
    )
    assert user.is_patient()
    assert user.check_password("testpass123")

@pytest.mark.django_db
def test_doctor_average_rating(user_patient, user_doctor, specialty, doctor_profile):
    appointment_1 = Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=10),
        time=datetime.time(15, 0),
        reason="Rotina",
        status="completed"
    )

    appointment_2 = Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=2),
        time=datetime.time(10, 0),
        reason="Rotina",
        status="completed"
    )

    AppointmentFeedback.objects.create(appointment=appointment_1, rating=5, comment="Great")
    AppointmentFeedback.objects.create(appointment=appointment_2, rating=3, comment="Ok")
    avg = doctor_profile.average_rating()
    assert avg == 4