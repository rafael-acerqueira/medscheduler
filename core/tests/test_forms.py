import pytest
from django.urls import reverse
from core.forms import AppointmentForm, AppointmentFeedbackForm
from core.models import Appointment, Specialty, PatientProfile, DoctorProfile
from django.contrib.auth import get_user_model
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


def test_appointment_form_rejects_holiday(user_patient, user_doctor, specialty, doctor_profile, settings):
    holiday = datetime.date(2025, 12, 25)
    data = {
        "specialty": specialty.pk,
        "doctor": user_doctor.pk,
        "date": holiday,
        "time": "09:00",
        "reason": "Checkup",
    }
    form = AppointmentForm(data=data, user=user_patient)
    assert not form.is_valid()
    assert "Appointments cannot be scheduled on holidays." in str(form.errors)

@pytest.mark.django_db
def test_feedback_form_valid(appointment):
    data = {"rating": 4, "comment": "Awesome Doctor"}
    form = AppointmentFeedbackForm(data=data)
    assert form.is_valid()

@pytest.mark.django_db
def test_feedback_form_rating_out_of_range(appointment):
    data = {"rating": 6}
    form = AppointmentFeedbackForm(data=data)
    assert not form.is_valid()
    assert "rating" in form.errors

@pytest.mark.django_db
def test_register_patient_get_renders_form(client):
    resp = client.get(reverse("register_patient"))
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Create your account" in html
    assert 'name="cpf"' in html



User = get_user_model()

@pytest.mark.django_db
def test_register_patient_success_creates_user_and_profile_and_logs_in(client):
    resp = client.post(reverse("register_patient"), {
        "username": "patient_new",
        "email": "pnew@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "cpf": "12345678901",
    })
    assert resp.status_code == 302

    user = User.objects.get(username="patient_new")
    assert user.role == User.PATIENT
    prof = PatientProfile.objects.get(user=user)
    assert prof.cpf == "12345678901"

@pytest.mark.django_db
def test_register_patient_password_mismatch_shows_error(client):
    resp = client.post(reverse("register_patient"), {
        "username": "patient_fail",
        "email": "pfail@example.com",
        "password": "StrongPass123",
        "password2": "Mismatch123",
        "cpf": "12345678902",
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Passwords do not match" in html


@pytest.mark.django_db
def test_register_patient_missing_cpf_shows_error(client):
    resp = client.post(reverse("register_patient"), {
        "username": "patient_nocpf",
        "email": "nocpf@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "CPF is required." in html


@pytest.mark.django_db
def test_register_patient_cpf_uniqueness_error(client):

    client.post(reverse("register_patient"), {
        "username": "patient_a",
        "email": "a@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "cpf": "12345678903",
    })

    resp = client.post(reverse("register_patient"), {
        "username": "patient_b",
        "email": "b@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "cpf": "12345678903",
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "already in use" in html or "already" in html




@pytest.mark.django_db
def test_register_doctor_get_renders_form(client):
    resp = client.get(reverse("register_doctor"))
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Create your account" in html
    assert 'name="crm"' in html


@pytest.mark.django_db
def test_register_doctor_success_creates_user_and_profile_and_logs_in(client):
    resp = client.post(reverse("register_doctor"), {
        "username": "doctor_new",
        "email": "dnew@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "crm": "CRM12345",
    })
    assert resp.status_code == 302

    user = User.objects.get(username="doctor_new")
    assert user.role == User.DOCTOR
    prof = DoctorProfile.objects.get(user=user)
    assert prof.crm == "CRM12345"


@pytest.mark.django_db
def test_register_doctor_password_mismatch_shows_error(client):
    resp = client.post(reverse("register_doctor"), {
        "username": "doctor_fail",
        "email": "dfail@example.com",
        "password": "StrongPass123",
        "password2": "Mismatch123",
        "crm": "CRM54321",
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Passwords do not match" in html


@pytest.mark.django_db
def test_register_doctor_missing_crm_shows_error(client):
    resp = client.post(reverse("register_doctor"), {
        "username": "doctor_nocrm",
        "email": "nocrm@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        # sem crm
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "CRM is required." in html


@pytest.mark.django_db
def test_register_doctor_crm_uniqueness_error(client):
    client.post(reverse("register_doctor"), {
        "username": "doctor_a",
        "email": "a@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "crm": "CRM999",
    })
    resp = client.post(reverse("register_doctor"), {
        "username": "doctor_b",
        "email": "b@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123",
        "crm": "CRM999",
    })
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "already in use" in html or "already" in html