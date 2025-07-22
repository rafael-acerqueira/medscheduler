from django.contrib import admin
from .models import Specialty, Appointment

admin.site.register(Specialty)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'specialty', 'date', 'time', 'status']
    list_filter = ['doctor', 'specialty', 'status', 'date']
    search_fields = ['patient__username', 'doctor__username', 'reason']
    ordering = ['-date', 'time']