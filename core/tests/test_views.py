import pytest
from django.urls import reverse
from django.utils import timezone
from core.models import User, Appointment, AppointmentFeedback
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

@pytest.mark.django_db
def test_patient_can_leave_feedback(client, user_patient, appointment):
    appointment.status = "completed"
    appointment.save()
    client.force_login(user_patient)
    url = reverse('leave_feedback', kwargs={"appointment_id": appointment.pk})
    resp = client.post(url, {"rating": 4, "comment": "Legal!"})
    assert resp.status_code == 302

@pytest.mark.django_db
def test_patient_cannot_leave_feedback_twice(client, user_patient, appointment):
    appointment.status = "completed"
    appointment.save()
    client.force_login(user_patient)
    url = reverse('leave_feedback', kwargs={"appointment_id": appointment.pk})
    client.post(url, {"rating": 5})
    resp = client.post(url, {"rating": 3})
    assert resp.status_code in (403, 400, 302)

@pytest.mark.django_db
def test_cannot_leave_feedback_unfinished_appointment(client, user_patient, appointment):
    appointment.status = "confirmed"
    appointment.save()
    client.force_login(user_patient)
    url = reverse('leave_feedback', kwargs={"appointment_id": appointment.pk})
    resp = client.post(url, {"rating": 5, "comment": "I can't leave feedback until complete"})
    assert resp.status_code in (403, 400, 302)


@pytest.mark.django_db
def test_average_rating_displayed(client, user_doctor, user_patient, specialty):

    appointment = Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() - datetime.timedelta(days=1),
        time=datetime.time(10, 0),
        reason="Checkup",
        status="completed"
    )
    AppointmentFeedback.objects.create(appointment=appointment, rating=4, comment="Great Service!")

    client.force_login(user_doctor)
    response = client.get("/")
    assert response.status_code == 200
    assert "⭐ Average rating" in response.content.decode()
    assert "4.0" in response.content.decode()


@pytest.mark.django_db
def test_monthly_appointments_count(client, user_doctor, user_patient, specialty):
    today = timezone.now().date()
    Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=today,
        time=datetime.time(10, 0),
        reason="Checkup",
        status="completed"
    )

    client.force_login(user_doctor)
    response = client.get("/")
    assert response.status_code == 200
    assert "Appointments this month" in response.content.decode()
    assert "1" in response.content.decode()


@pytest.mark.django_db
def test_most_common_specialties_display(client, user_doctor, user_patient, specialty):
    user_doctor.doctorprofile.specialties.add(specialty)

    Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date(),
        time=datetime.time(9, 0),
        reason="Checkup",
        status="confirmed"
    )
    Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=1),
        time=datetime.time(10, 0),
        reason="Checkup",
        status="confirmed"
    )

    client.force_login(user_doctor)
    response = client.get("/")
    assert response.status_code == 200
    assert "Most frequent specialties" in response.content.decode()
    assert specialty.name in response.content.decode()

@pytest.mark.django_db
def test_patient_dashboard_metrics_display(client, user_patient, user_doctor, specialty):

    Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() + datetime.timedelta(days=3),
        time=datetime.time(10, 0),
        status='confirmed'
    )

    past_appointment = Appointment.objects.create(
        patient=user_patient,
        doctor=user_doctor,
        specialty=specialty,
        date=timezone.now().date() - datetime.timedelta(days=2),
        time=datetime.time(9, 0),
        status='completed'
    )
    AppointmentFeedback.objects.create(appointment=past_appointment, rating=5, comment="Excelente")

    client.force_login(user_patient)
    response = client.get(reverse("dashboard"))
    html = response.content.decode()

    assert response.status_code == 200
    assert "Your metrics" in html
    assert "Upcoming appointments" in html
    assert "Past appointments" in html
    assert "Average rating you gave" in html
    assert "Most visited doctors" in html
    assert "5.0" in html  # rating
    assert user_doctor.get_full_name() in html or user_doctor.username in html