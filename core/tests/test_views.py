import pytest
from django.urls import reverse
from django.utils import timezone
from core.models import User, Appointment
import datetime

def get_next_weekday(start_date, allowed_days=(0, 1, 2, 3, 4)):
    date = start_date
    while date.weekday() not in allowed_days:
        date += datetime.timedelta(days=1)
    return date

@pytest.mark.django_db
def test_login_view(client, user_patient):
    response = client.post(reverse('login'), {
        'username': user_patient.username,
        'password': 'testpass123'
    })
    assert response.status_code == 302


import pytest

@pytest.mark.django_db
def test_patient_can_cancel_own_appointment(appointment, client, user_patient):
    client.force_login(user_patient)
    response = client.post(f"/appointments/{appointment.id}/cancel/")
    appointment.refresh_from_db()
    assert response.status_code == 302
    assert appointment.status == "cancelled"

@pytest.mark.django_db
def test_patient_cannot_cancel_others_appointment(appointment, client, django_user_model):
    other_user = django_user_model.objects.create_user(username="other", password="pass", role=User.PATIENT)
    client.force_login(other_user)
    response = client.post(f"/appointments/{appointment.id}/cancel/")
    appointment.refresh_from_db()
    assert appointment.status != "cancelled"
    assert response.status_code in (403, 302, 404)

@pytest.mark.django_db
def test_cannot_cancel_cancelled_appointment(appointment, client, user_patient):
    appointment.status = "cancelled"
    appointment.save()
    client.force_login(user_patient)
    response = client.post(f"/appointments/{appointment.id}/cancel/")

    appointment.refresh_from_db()
    assert appointment.status == "cancelled"

@pytest.mark.django_db
def test_patient_can_reschedule_appointment(appointment, client, user_patient):
    client.force_login(user_patient)
    today = timezone.now().date()
    new_date = get_next_weekday(today + datetime.timedelta(days=2))
    new_time = datetime.time(11, 0)
    response = client.post(
        f"/appointments/{appointment.id}/reschedule/",
        {"date": new_date, "time": new_time}
    )
    appointment.refresh_from_db()
    assert response.status_code == 302
    assert appointment.date == new_date
    assert appointment.time == new_time

@pytest.mark.django_db
def test_cannot_reschedule_to_past_date(appointment, client, user_patient):
    client.force_login(user_patient)
    past_date = timezone.now().date() - datetime.timedelta(days=1)
    response = client.post(
        f"/appointments/{appointment.id}/reschedule/",
        {"date": past_date, "time": datetime.time(10, 0)}
    )
    appointment.refresh_from_db()
    assert appointment.date != past_date
    assert b"Cannot schedule for a past date" in response.content or response.status_code == 200

@pytest.mark.django_db
def test_patient_cannot_cancel_others_appointment(client, user_patient, user_doctor, specialty, doctor_profile):

    other_patient = User.objects.create_user(
        username="other_patient", password="testpass", role=User.PATIENT, is_active=True
    )
    appointment = Appointment.objects.create(
        patient=other_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=datetime.date(2025, 8, 2),
        time=datetime.time(9, 0),
        reason="For testing",
        status="confirmed",
    )
    client.force_login(user_patient)
    url = reverse("appointment_cancel", kwargs={"pk": appointment.pk})
    response = client.post(url)
    assert response.status_code in (403, 404)