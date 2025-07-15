from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User, PatientProfile, DoctorProfile

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

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['crm', 'specialty']
        labels = {
            'crm': 'CRM',
            'specialty': 'Specialty'
        }
        widgets = {
            'crm': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your CRM',
                'autocomplete': 'crm',
            }),
            'specialty': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your Specialty',
                'autocomplete': 'specialty',
            })
        }