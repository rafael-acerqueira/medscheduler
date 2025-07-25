from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import UserRegistrationForm, PatientProfileForm, DoctorProfileForm, UserEditForm, ConfirmPasswordForm, \
    AppointmentForm, AvailabilitySearchForm
from .models import User, Appointment, DoctorProfile

import datetime


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
        form = AvailabilitySearchForm()

    return render(request, 'find_available.html', {
        'form': form,
        'slots': slots,
    })
