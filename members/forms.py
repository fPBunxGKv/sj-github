from django import forms
from .models import sj_users

# create a ModelForm
class RegisterUserForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
    
    # specify the name of model to use
    class Meta:
        model = sj_users
        fields = [
            'firstname', 'lastname', 'byear', 'gender', 'email', 'phone', 'city'
        ]
        
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                'required': True,
                }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                'required': True,
                }),
            'byear': forms.NumberInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                'required': True,
                }),
            'gender': forms.Select(attrs={'class': 'form-control', 'required': True, 'type': 'radio'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                'required': True,
                }),
            'phone': forms.TextInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                }),
            'city': forms.TextInput(attrs={
                'class': 'form-outline',
                'class': 'form-control form-control-lg',
                'required': True,
                }),
        }

        labels = {
            'firstname': "Vorname",
            'lastname': "Nachname",
            'byear' : 'Jahrgang',
            'gender' : 'Geschlecht',
            'email' : 'E-Mail',
            'phone' : 'Telefon',
            'city' : 'Ort',
        }
    def clean(self):
            data = self.cleaned_data
