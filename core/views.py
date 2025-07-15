from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, PatientProfileForm, DoctorProfileForm


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
        return redirect('home')


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