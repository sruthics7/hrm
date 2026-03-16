from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserGroup
from django.forms import ModelForm, inlineformset_factory
from .models import Module, Child,SubChild,SubSubChild
from .models import Employee
from .models import LeaveRequest
from django.utils import timezone
from datetime import timedelta



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
USERGROUP_CHOICES = [
    ('Admin', 'Admin'),
    ('Employee', 'Employee'),
   
]
class RegistrationForm(UserCreationForm):
    usergroup = forms.ChoiceField(
        choices=USERGROUP_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter name'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password'
            }),
        }

    def __init__(self, *args, **kwargs):
        profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        # Optional: Pre-fill fields if editing
        if profile_instance:
            self.fields['name'].initial = profile_instance.name
            self.fields['usergroup'].initial = profile_instance.usergroup
            self.fields['image'].initial = profile_instance.image
            
class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            
        }

class ModuleForm(ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'url_name', 'icon_class']
class ChildForm(forms.ModelForm):       
    class Meta:
        model = Child
        fields = ['module', 'name', 'url_name']  # Include icon_class here

class SubChildForm(forms.ModelForm):
    class Meta:
        model = SubChild
        fields = ['child', 'name', 'url_name']  # Include icon_class here

class SubSubChildForm(forms.ModelForm):
    class Meta:
        model = SubSubChild
        fields = ['subchild', 'name', 'url_name']  # Include icon_class here        

ChildFormSet = inlineformset_factory(Module, Child, fields=('name', 'url_name'), extra=1, can_delete=True)

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'date_of_birth', 'blood_group',
            'joining_date', 'designation', 'department',
            'email', 'phone', 'emergency_number', 'salary'
        ]

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'


class LeaveRequestForm(forms.ModelForm):

    class Meta:
        model = LeaveRequest
        fields = [
            'leave_type',
            'start_date',
            'end_date',
            'reason',
            'medical_proof'
        ]

    def clean(self):
        cleaned_data = super().clean()

        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        medical_proof = cleaned_data.get('medical_proof')

        today = timezone.now().date()

        # ✅ Casual Leave → 2 days advance
        if leave_type == 'CL':
            if start_date < today + timedelta(days=2):
                raise forms.ValidationError(
                    "Casual Leave must be applied at least 2 days in advance."
                )

        # ✅ Medical Leave → proof required
        if leave_type == 'ML':
            if not medical_proof:
                raise forms.ValidationError(
                    "Medical proof is required for Medical Leave."
                )

        # ✅ Emergency Leave → max 2 days
        if leave_type == 'EL':
            if start_date and end_date:
                duration_days = (end_date - start_date).days + 1
                if duration_days > 60:
                    raise forms.ValidationError(
                        "Emergency Leave cannot exceed 2 months (60 days). "
                        "For longer durations please use Earned/Privilege Leave "
                        "or contact HR."
                    )
            elif start_date and not end_date:
                # single day → always allowed for EL
                pass
        return cleaned_data