import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_view(client, user_patient):
    response = client.post(reverse('login'), {
        'username': user_patient.username,
        'password': 'testpass123'
    })
    assert response.status_code == 302
