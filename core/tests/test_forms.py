import pytest
from core.forms import AppointmentForm
from core.models import Appointment


@pytest.mark.django_db
def test_appointment_form_valid(user_patient, user_doctor, specialty, doctor_profile):
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2027-08-05",
        "time": "09:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    print(form.errors)
    assert form.is_valid()


@pytest.mark.django_db
def test_duplicate_appointment_not_allowed(user_patient, user_doctor, specialty):
    Appointment.objects.create(
        specialty=specialty,
        doctor=user_doctor,
        patient=user_patient,
        date="2025-08-02",
        time="09:00",
        status="confirmed"
    )
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2025-08-02",
        "time": "09:00",
        "reason": "Another",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert "already has an appointment" in str(form.errors)