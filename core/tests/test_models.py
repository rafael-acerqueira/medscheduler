import pytest
from core.models import User, Specialty, Appointment

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
