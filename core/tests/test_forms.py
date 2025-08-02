import pytest
from core.forms import AppointmentForm
from core.models import Appointment, Specialty
import datetime

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

@pytest.mark.django_db
def test_appointment_form_date_in_past(user_patient, user_doctor, specialty, doctor_profile):
    doctor_profile.crm = "12345"
    doctor_profile.save()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": yesterday,
        "time": "09:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert 'date' in form.errors or '__all__' in form.errors


@pytest.mark.django_db
def test_appointment_form_out_of_hours(user_patient, user_doctor, specialty, doctor_profile):
    doctor_profile.crm = "12345"
    doctor_profile.save()
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2025-08-02",
        "time": "22:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert 'time' in form.errors or '__all__' in form.errors

@pytest.mark.django_db
def test_appointment_form_double_booking(user_patient, user_doctor, specialty, doctor_profile):
    doctor_profile.crm = "12345"
    doctor_profile.save()
    Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date="2025-08-02",
        time="09:00",
        reason="Previous",
        status="confirmed"
    )
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2025-08-02",
        "time": "09:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert '__all__' in form.errors

@pytest.mark.django_db
def test_appointment_form_doctor_inactive(user_patient, user_doctor, specialty, doctor_profile):
    doctor_profile.crm = "12345"
    doctor_profile.save()
    user_doctor.is_active = False
    user_doctor.save()
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2025-08-02",
        "time": "10:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert '__all__' in form.errors


@pytest.mark.django_db
def test_appointment_form_doctor_wrong_specialty(user_patient, user_doctor, specialty, doctor_profile):
    doctor_profile.crm = "12345"
    doctor_profile.save()
    another_specialty = Specialty.objects.create(name="Dermatology")
    data = {
        "specialty": another_specialty.pk,
        "doctor": user_doctor.pk,
        "date": "2025-08-02",
        "time": "10:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert '__all__' in form.errors
