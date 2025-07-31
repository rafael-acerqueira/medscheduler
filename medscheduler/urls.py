"""
URL configuration for medscheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core.forms import CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
from core.views import register, profile, edit_profile, user_list, edit_profile_admin, toggle_user_status, \
    delete_account, schedule_appointment, doctors_by_specialty, find_available_doctors, appointment_list, \
    appointment_detail, appointment_cancel, appointment_reschedule, export_appointments_csv, doctor_appointments, \
    doctor_appointment_detail, export_doctor_appointments_csv, leave_feedback, CustomLoginView, dashboard, triage

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit-profile'),
    path('users/', user_list, name='user-list'),
    path('users/<int:user_id>/edit/', edit_profile_admin, name='edit-profile-admin'),
    path('users/<int:user_id>/toggle/', toggle_user_status, name='toggle-user-status'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', form_class=CustomPasswordResetForm),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', form_class=CustomSetPasswordForm),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html', form_class=CustomPasswordChangeForm),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),
    path('delete_account/',delete_account, name='delete_account'),
    path('appointments/schedule/', schedule_appointment, name='schedule_appointment'),
    path('ajax/doctors_by_specialty/', doctors_by_specialty, name='doctors_by_specialty'),
    path('availability/', find_available_doctors, name='find_available_doctors'),
    path('my-appointments/', appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/', appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:pk>/reschedule/', appointment_reschedule, name='appointment_reschedule'),
    path('my-appointments/export/', export_appointments_csv, name='export_appointments_csv'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('doctor/appointments/<int:pk>/', doctor_appointment_detail, name='doctor_appointment_detail'),
    path('doctor/appointments/export/', export_doctor_appointments_csv, name='export_doctor_appointments_csv'),
    path('appointments/<int:appointment_id>/feedback/', leave_feedback, name='leave_feedback'),
    path('triage/', triage, name='triage')
]
