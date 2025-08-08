import csv
import requests
from django.conf import settings
from collections import Counter
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q,Avg
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils import timezone
from .forms import UserRegistrationForm, PatientProfileForm, DoctorProfileForm, UserEditForm, ConfirmPasswordForm, \
    AppointmentForm, AvailabilitySearchForm, AppointmentRescheduleForm, AppointmentFeedbackForm, LoginForm
from .models import User, Appointment, DoctorProfile, Specialty

import datetime
from datetime import date


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user

    if user.is_patient():
        profile = getattr(user, 'patientprofile', None)
        form_class = PatientProfileForm
    elif user.is_doctor():
        profile = getattr(user, 'doctorprofile', None)
        form_class = DoctorProfileForm
    else:
        return redirect('/admin/')


    if profile is None:
        profile = form_class.Meta.model.objects.create(user=user)

    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = form_class(instance=profile)

    return render(request, 'profile.html', {'form': form, 'user_obj': user})

@login_required
def edit_profile(request):
    user = request.user

    if user.is_patient():
        profile = getattr(user, 'patientprofile', None)
        profile_form_class = PatientProfileForm
    elif user.is_doctor():
        profile = getattr(user, 'doctorprofile', None)
        profile_form_class = DoctorProfileForm
    else:
        profile = None
        profile_form_class = None

    if profile is None:
        messages.error(request, "Profile not found.")
        return redirect('profile')  # ou home

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = profile_form_class(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('edit-profile')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = profile_form_class(instance=profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user,
    })


def is_authenticated_admin(user):
    return user.is_authenticated and user.is_admin()

@user_passes_test(is_authenticated_admin)
def edit_profile_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)

    profile = None
    profile_form = None

    if user.is_patient():
        profile = getattr(user, 'patientprofile', None)
        profile_form_class = PatientProfileForm
    elif user.is_doctor():
        profile = getattr(user, 'doctorprofile', None)
        profile_form_class = DoctorProfileForm
    else:
        profile_form_class = None

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        if profile_form_class and profile:
            profile_form = profile_form_class(request.POST, instance=profile)
        else:
            profile_form = None

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            return redirect('user-list')
    else:
        user_form = UserEditForm(instance=user)
        if profile_form_class and profile:
            profile_form = profile_form_class(instance=profile)
        else:
            profile_form = None

    return render(request, 'edit_profile_admin.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user,
    })

@user_passes_test(is_authenticated_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('user-list')

@user_passes_test(is_authenticated_admin)
def user_list(request):
    users = User.objects.all()
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    if role:
        users = users.filter(role=role)

    users = users.order_by('first_name', 'last_name')


    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'users': page_obj,
        'search': search,
        'role': role,
        'role_choices': User.ROLE_CHOICES,
        'page_obj': page_obj,
    }
    return render(request, 'user_list.html', context)


@login_required
def delete_account(request):
    if request.method == 'POST':
        form = ConfirmPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = request.user
            if user.check_password(password):
                user.delete()
                messages.success(request, "Your account has been deleted. We're sorry to see you go!")
                logout(request)
                return redirect('login')
            else:
                messages.error(request, "Incorrect password. Please try again.")
    else:
        form = ConfirmPasswordForm()

    return render(request, 'account_delete_confirm.html', {'form': form})


@login_required
def schedule_appointment(request):
    if not request.user.is_patient():
        return redirect('dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('appointment_list')

    elif request.method == 'GET':
        initial = {}
        initial['doctor'] = request.GET.get('doctor')
        initial['specialty'] = request.GET.get('specialty')
        initial['date'] = request.GET.get('date')
        initial['time'] = request.GET.get('time')
        form = AppointmentForm(initial=initial, user=request.user)
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'schedule.html', {'form': form})


@login_required
def doctors_by_specialty(request):
    specialty_id = request.GET.get('specialty')
    doctors = User.objects.filter(
        role=User.DOCTOR,
        is_active=True,
        doctorprofile__specialties__id=specialty_id
    ).distinct()
    data = [
        {'id': doctor.id, 'name': doctor.get_full_name() or doctor.username}
        for doctor in doctors
    ]
    return JsonResponse({'doctors': data})


@login_required
def find_available_doctors(request):
    doctors = slots = None
    specialty_id = request.GET.get('specialty')
    if request.method == 'POST':
        form = AvailabilitySearchForm(request.POST)
        if form.is_valid():
            specialty = form.cleaned_data['specialty']
            date = form.cleaned_data['date']


            doctors = DoctorProfile.objects.filter(
                specialties=specialty,
                user__is_active=True,
                user__role='doctor'
            ).select_related('user')


            slots = {}
            for doctor in doctors:
                taken_times = set(
                    Appointment.objects.filter(
                        doctor=doctor.user,
                        date=date
                    ).values_list('time', flat=True)
                )
                slots_per_day = [datetime.time(h, m) for h in range(8, 18) for m in (0, 30)]
                free = [t for t in slots_per_day if t not in taken_times]
                if free:
                    slots[doctor] = free

    else:
        form = AvailabilitySearchForm(initial={'specialty': specialty_id})

    return render(request, 'find_available.html', {
        'form': form,
        'slots': slots
    })


@login_required
def appointment_list(request):

    appointments = Appointment.objects.filter(patient=request.user)

    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        appointments = appointments.filter(date__gte=start_date)
    if end_date:
        appointments = appointments.filter(date__lte=end_date)

    order_by = request.GET.get('order_by', 'date')
    order_dir = request.GET.get('order_dir', 'asc')
    if order_dir == 'desc':
        ordering = '-' + order_by
    else:
        ordering = order_by

    appointments = appointments.order_by(ordering)

    columns = [
        ('date', 'Date'),
        ('time', 'Time'),
        ('doctor', 'Doctor'),
        ('specialty', 'Specialty'),
        ('status', 'Status'),
        ('actions', 'Actions'),
    ]

    return render(request, 'patient_list.html', {
        'appointments': appointments,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'columns': columns,
        'order_by': order_by,
        'order_dir': order_dir,
        'today': date.today()
    })

@login_required
def appointment_detail(request, pk):

    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    return render(request, 'detail.html', {
        'appointment': appointment
    })


@login_required
def appointment_cancel(request, pk):
    time_limit_to_cancel = 86400

    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    now = timezone.now()
    dt_appointment = timezone.make_aware(
        datetime.datetime.combine(appointment.date, appointment.time),
        timezone.get_current_timezone()
    )
    can_cancel = (
            appointment.status == "confirmed" and
            (dt_appointment - now).total_seconds() > time_limit_to_cancel
    )
    if not can_cancel:
        messages.error(request, "You can only cancel appointments at least 24 hours in advance.")
        return redirect('appointment_detail', pk=pk)

    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('appointment_list')


    return render(request, "cancel_confirm.html", {"appointment": appointment})


@login_required
def appointment_reschedule(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)


    if not appointment.can_be_rescheduled:
        messages.error(request, "You cannot reschedule this appointment.")
        return redirect('appointment_detail', pk=pk)

    if request.method == "POST":
        form = AppointmentRescheduleForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            appointment.status = "confirmed"
            appointment.save()
            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('appointment_detail', pk=pk)
    else:
        form = AppointmentRescheduleForm(instance=appointment)

    return render(request, "reschedule.html", {"form": form, "appointment": appointment})

@login_required
def export_appointments_csv(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_appointments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Doctor', 'Specialty', 'Status', 'Reason'])

    for a in appointments:
        writer.writerow([
            a.date.strftime('%Y-%m-%d'),
            a.time.strftime('%H:%M'),
            a.doctor.get_full_name() if hasattr(a.doctor, 'get_full_name') else str(a.doctor),
            ", ".join(s.name for s in a.doctor.doctorprofile.specialties.all()) if hasattr(a.doctor, "doctorprofile") else "",
            a.get_status_display(),
            a.reason or ""
        ])
    return response


@login_required
def doctor_appointments(request):
    if not request.user.is_doctor():
        return redirect('dashboard')
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-date', '-time')

    status = request.GET.get('status')
    patient_name = request.GET.get('patient')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if status:
        appointments = appointments.filter(status=status)
    if patient_name:
  
        search_parts = patient_name.strip().split()
        q = Q()
        for part in search_parts:
            q &= (
                    Q(patient__first_name__icontains=part) |
                    Q(patient__last_name__icontains=part) |
                    Q(patient__username__icontains=part) |
                    Q(patient__email__icontains=part)
            )
        appointments = appointments.filter(q)
    if start_date:
        appointments = appointments.filter(date__gte=start_date)
    if end_date:
        appointments = appointments.filter(date__lte=end_date)

    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'doctor/appointments.html', {
        'page_obj': page_obj,
        'status': status,
        'patient_name': patient_name,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def doctor_appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    if request.method == "POST" and 'complete' in request.POST:
        if appointment.status == "confirmed":
            appointment.status = "completed"
            appointment.save()
            messages.success(request, "Appointment marked as completed.")
            return redirect('doctor_appointments')
    return render(request, "doctor/appointment_detail.html", {'appointment': appointment})


@login_required
def export_doctor_appointments_csv(request):
    if not request.user.is_doctor():
        return redirect('dashboard')
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-date', '-time')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_agenda.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Patient', 'Status', 'Reason'])
    for a in appointments:
        writer.writerow([
            a.date.strftime('%Y-%m-%d'),
            a.time.strftime('%H:%M'),
            a.patient.get_full_name() if hasattr(a.patient, 'get_full_name') else str(a.patient),
            a.get_status_display(),
            a.reason or ""
        ])
    return response

@login_required
def leave_feedback(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if hasattr(appointment, 'feedback'):
        return redirect('appointment_detail', pk=appointment.id)

    if request.method == 'POST':
        form = AppointmentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.appointment = appointment
            feedback.save()
            messages.success(request, 'Feedback sent!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentFeedbackForm()
    return render(request, 'leave_feedback.html', {'form': form, 'appointment': appointment})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user
        if not user.has_completed_profile():
            return reverse('profile')
        return reverse('dashboard')


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    if user.is_patient():
        upcoming = Appointment.objects.filter(patient=user, date__gte=today).order_by('date', 'time')[:5]
        recent = Appointment.objects.filter(patient=user, date__lt=today).order_by('-date', '-time')[:5]
        upcoming_count = Appointment.objects.filter(patient=user, date__gte=today).count()
        past_count = Appointment.objects.filter(patient=user, date__lt=today).count()

        result = Appointment.objects.filter(
            patient=user,
            feedback__isnull=False
        ).aggregate(avg_rating=Avg('feedback__rating'))
        average_given_rating = round(result['avg_rating'] or 0, 2)

        doctors = [
            a.doctor.get_full_name() if hasattr(a.doctor, "get_full_name") else str(a.doctor)
            for a in Appointment.objects.filter(patient=user)
        ]
        most_visited_doctors = Counter(doctors).most_common(3)

        return render(request, 'dashboard_patient.html', {
            'upcoming': upcoming,
            'recent': recent,
            'upcoming_count': upcoming_count,
            'past_count': past_count,
            'average_given_rating': average_given_rating,
            'most_visited_doctors': most_visited_doctors,
        })
    elif user.is_doctor():
        upcoming = Appointment.objects.filter(doctor=user, date__gte=today).order_by('date', 'time')[:5]
        feedbacks = Appointment.objects.filter(doctor=user, status='completed', feedback__isnull=False).order_by('-date', '-time')[:5]
        average_rating = Appointment.objects.filter(doctor=user, status='completed', feedback__isnull=False
                         ).aggregate(avg_rating=Avg('feedback__rating'))['avg_rating'] or 0
        monthly_appointments = Appointment.objects.filter(
                                                            doctor=user,
                                                            status='completed',
                                                            date__month=today.month,
                                                            date__year=today.year
                                                        ).count()
        specialties = [
                                                    s.name
                                                    for a in Appointment.objects.filter(doctor=user)
                                                    for s in a.doctor.doctorprofile.specialties.all()
                                                ]
        most_common_specialties = Counter(specialties).most_common(3)
        return render(request, 'dashboard_doctor.html', {
            'upcoming': upcoming,
            'feedbacks': feedbacks,
            'average_rating': round(average_rating, 2),
            'monthly_appointments': monthly_appointments,
            'most_common_specialties': most_common_specialties
        })
    elif user.is_admin:
        User = get_user_model()
        metrics = {
            'total_users': User.objects.count(),
            'total_patients': User.objects.filter(role=User.PATIENT).count(),
            'total_doctors': User.objects.filter(role=User.DOCTOR).count(),
            'total_admins': User.objects.filter(role=User.ADMIN).count(),
            'total_appointments': Appointment.objects.count(),
            'appointments_today': Appointment.objects.filter(date=today).count(),
            'appointments_confirmed': Appointment.objects.filter(status='confirmed').count(),
            'appointments_cancelled': Appointment.objects.filter(status='cancelled').count(),
            'total_specialties': Specialty.objects.count(),
            'recent_users': User.objects.order_by('-date_joined')[:5],
        }
        return render(request, 'dashboard_admin.html', {'metrics': metrics})
    else:
        return redirect('login')


def normalize_specialty(label):
    label_clean = label.strip().title()
    try:
        return Specialty.objects.get(name__iexact=label_clean)
    except Specialty.DoesNotExist:
        return None

def triage(request):
    suggestion = None
    suggested_specialty = None
    error = None
    SPECIALTIES = list(Specialty.objects.filter(is_active=True).values_list('name', flat=True))

    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        if not symptoms:
            error = "Please enter your symptoms."
        else:
            API_URL = "https://api-inference.huggingface.co/models/joeddav/xlm-roberta-large-xnli"
            headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}
            payload = {
                "inputs": symptoms,
                "parameters": {"candidate_labels": SPECIALTIES}
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                result = response.json()

                if "labels" in result and result["labels"]:
                    suggestion = result["labels"][0]
                    suggested_specialty = normalize_specialty(suggestion)
                else:
                    error = "The AI could not suggest a specialty."
            except Exception as ex:
                print(ex)
                error = "An error occurred while contacting the AI service."

    return render(request, "triage.html", {
        "suggestion": suggestion,
        "suggested_specialty": suggested_specialty,
        "error": error,
    })
