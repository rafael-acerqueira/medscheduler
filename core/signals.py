from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PatientProfile, DoctorProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.PATIENT:
            PatientProfile.objects.create(user=instance)
        elif instance.role == User.DOCTOR:
            DoctorProfile.objects.create(user=instance)