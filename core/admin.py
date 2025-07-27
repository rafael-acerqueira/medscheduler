from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
import csv

from .models import Specialty, Appointment

admin.site.register(Specialty)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    def colored_status(self, obj):
        color_map = {
            "confirmed": "#2563eb",
            "completed": "#16a34a",
            "cancelled": "#6b7280",
            "pending": "#eab308",
        }
        color = color_map.get(obj.status, "#374151")
        label = obj.get_status_display()
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    colored_status.short_description = "Status"

    def export_appointments_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="appointments.csv"'
        writer = csv.writer(response)
        writer.writerow(['Patient', 'Doctor', 'Specialty', 'Date', 'Time', 'Status'])
        for obj in queryset:
            writer.writerow([
                obj.patient.get_full_name() or obj.patient.username,
                obj.doctor.get_full_name() or obj.doctor.username,
                obj.specialty.name if obj.specialty else '',
                obj.date,
                obj.time,
                obj.get_status_display()
            ])
        return response

    export_appointments_csv.short_description = "Export selected appointments to CSV"

    list_filter = ['doctor', 'specialty', 'status', 'date']
    search_fields = [
        'patient__username', 'patient__first_name', 'patient__last_name', 'patient__email',
        'doctor__username', 'doctor__first_name', 'doctor__last_name', 'doctor__email',
        'reason'
    ]
    ordering = ['-date', 'time']
    list_display = ['patient', 'doctor', 'specialty', 'date', 'time', 'status']
    actions = [export_appointments_csv]