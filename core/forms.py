import datetime
from datetime import date

from django.utils import timezone

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm

from .models import User, PatientProfile, DoctorProfile, Specialty, Appointment, AppointmentFeedback

ROLE_CHOICES = [user_role for user_role in User.ROLE_CHOICES if user_role[0] != User.ADMIN]

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Repeat your password',
            'autocomplete': 'new-password',
        })
    )
    role = forms.ChoiceField(
        label="Role",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your username',
                'autocomplete': 'username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your email',
                'autocomplete': 'email',
            }),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Email address'
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['cpf', 'birthdate', 'health_plan']
        labels = {
            'cpf': 'CPF',
            'birthdate': 'Birthdate',
            'health_plan': 'Health Plan'
        }
        widgets = {
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your CPF',
                'autocomplete': 'cpf',
                'label': 'CPF'
            }),
            'health_plan': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your Health Plan',
                'autocomplete': 'health_plan',
            }),
            'birthdate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select your birthdate',
                'autocomplete': 'bday',
            })
        }

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        qs = PatientProfile.objects.filter(cpf=cpf)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("There is already a patient with this CPF.")
        return cpf

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['crm', 'specialties']
        labels = {
            'crm': 'CRM',
            'specialties': 'Specialties'
        }
        widgets = {
            'crm': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your CRM',
                'autocomplete': 'crm',
            }),
            'specialties': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your Specialty',
                'autocomplete': 'specialty',
            })
        }

    def clean_crm(self):
        crm = self.cleaned_data['crm']
        qs = DoctorProfile.objects.filter(crm=crm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("There is already a doctor with this CRM.")
        return crm


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter new password'
        }),
        help_text="Enter a strong password."
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Repeat new password'
        }),
        help_text="Enter the same password as before, for verification."
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your current password',
        }),
    )
    new_password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter new password',
        }),
        help_text="Enter a strong password.",
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Repeat new password',
        }),
        help_text="Enter the same password as before, for verification.",
    )


class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your password'
        }),
        help_text="Type your password to confirm this action."
    )




WORK_START_HOUR = 8
WORK_END_HOUR = 18
DISABLED_WEEKDAYS = [5, 6]  # 5 = Saturday, 6 = Sunday
HOLIDAYS = [  # yyyy-mm-dd
    '2024-12-25',
    '2025-01-01',
]

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['specialty', 'doctor', 'date', 'time', 'reason']
        widgets = {
            'specialty': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a specialty'
            }),
            'doctor': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a doctor'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a date',
                'autocomplete': 'off',
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a time',
                'autocomplete': 'off',
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Describe the reason for your appointment',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['doctor'].queryset = User.objects.filter(role=User.DOCTOR, is_active=True)
        self.fields['specialty'].queryset = Specialty.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        specialty = cleaned_data.get('specialty')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        patient = self.user

        if doctor and date and time:
            if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
                raise forms.ValidationError("This doctor already has an appointment at this date and time.")


        if date and time:
            dt = datetime.datetime.combine(date, time)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            if dt < timezone.now():
                raise forms.ValidationError("Cannot schedule for a past date and time.")

        if time:
            if not (WORK_START_HOUR <= time.hour < WORK_END_HOUR):
                raise forms.ValidationError(f"Appointments can only be scheduled between {WORK_START_HOUR}:00 and {WORK_END_HOUR}:00.")


        if date:
            if date.weekday() in DISABLED_WEEKDAYS:
                raise forms.ValidationError("Appointments cannot be scheduled on weekends.")
            if date.strftime("%Y-%m-%d") in HOLIDAYS:
                raise forms.ValidationError("Appointments cannot be scheduled on holidays.")

        if patient and date:
            max_per_day = 2
            count = Appointment.objects.filter(patient=patient, date=date).count()
            if count >= max_per_day:
                raise forms.ValidationError("You have reached the limit of appointments for this day.")

        max_cancellations = 2
        days_window = 30
        recent_cancels = Appointment.objects.filter(
            patient=patient,
            status='cancelled',
            date__gte=timezone.now().date() - datetime.timedelta(days=days_window)
        ).count()
        if recent_cancels >= max_cancellations:
            raise forms.ValidationError(
                f"You have reached the limit of {max_cancellations} cancellations in the last {days_window} days."
            )

        if doctor and date and time:
            exists = Appointment.objects.filter(
                doctor=doctor,
                patient=patient,
                date=date,
                time=time
            ).exclude(status='cancelled').exists()
            if exists:
                raise forms.ValidationError(
                    "You already have an appointment with this doctor at this date and time."
                )

        if doctor and not doctor.is_active:
            raise forms.ValidationError("This doctor is not currently available.")

        if doctor and specialty:
            try:
                has_specialty = doctor.doctorprofile.specialties.filter(pk=specialty.pk).exists()
            except AttributeError:
                has_specialty = False
            if not has_specialty:
                raise forms.ValidationError("Selected doctor does not have this specialty.")

        required_fields = ['doctor', 'specialty', 'date', 'time']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")


        return cleaned_data

class AvailabilitySearchForm(forms.Form):
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Select a specialty'
        }),
        label="Specialty"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Select a date',
            'autocomplete': 'off'
        }),
        label="Date"
    )

    def clean_date(self):
        DISABLED_WEEKDAYS = (5, 6)
        MAX_DAYS_AHEAD = 60
        HOLIDAYS = ['2024-12-25', '2024-01-01']

        d = self.cleaned_data['date']
        today = date.today()
        if d < today:
            raise forms.ValidationError("Date cannot be in the past.")
        if d.weekday() in DISABLED_WEEKDAYS:
            raise forms.ValidationError("Appointments cannot be scheduled on weekends.")
        if (d - today).days > MAX_DAYS_AHEAD:
            raise forms.ValidationError(f"Please choose a date within the next {MAX_DAYS_AHEAD} days.")
        if d.strftime("%Y-%m-%d") in HOLIDAYS:
            raise forms.ValidationError("Appointments cannot be scheduled on holidays.")
        return d

class AppointmentRescheduleForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a date',
                'autocomplete': 'off',
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Select a time',
                'autocomplete': 'off',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        doctor = self.instance.doctor
        patient = self.instance.patient

        if doctor and date and time:
            exists = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=time
            ).exclude(pk=self.instance.pk).exists()
            if exists:
                raise forms.ValidationError("This doctor already has an appointment at this date and time.")


        if date and time:
            dt = datetime.datetime.combine(date, time)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            if dt < timezone.now():
                raise forms.ValidationError("Cannot schedule for a past date and time.")


        WORK_START_HOUR = 8
        WORK_END_HOUR = 18
        if time:
            if not (WORK_START_HOUR <= time.hour < WORK_END_HOUR):
                raise forms.ValidationError(
                    f"Appointments can only be scheduled between {WORK_START_HOUR}:00 and {WORK_END_HOUR}:00."
                )


        DISABLED_WEEKDAYS = [5, 6]
        if date:
            if date.weekday() in DISABLED_WEEKDAYS:
                raise forms.ValidationError("Appointments cannot be scheduled on weekends.")


        return cleaned_data

class AppointmentFeedbackForm(forms.ModelForm):
    class Meta:
        model = AppointmentFeedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border rounded',
            }),
        }