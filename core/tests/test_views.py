import pytest
from django.urls import reverse
from core.models import User

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

