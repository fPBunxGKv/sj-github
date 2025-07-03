from django import forms
from .models import sj_users,sj_results
from django.core.exceptions import ValidationError
import re
from datetime import date

NAME_REGEX = "^[a-zA-ZÀ-ÿ]+(?:[- ][a-zA-ZÀ-ÿ]+)*$"

class RegisterRunsForm(forms.ModelForm):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # specify the name of model to use
    class Meta:
        model = sj_results
        fields = [
            'fk_sj_users', 'fk_sj_events', 'run_nr', 'line_nr', 'result', 'result_category', 'state'
        ]

    def clean(self):
        #data = self.cleaned_data
        cleaned_data = super().clean()

        return cleaned_data

# RegisterUserForm is used to register a new user
# if lastname and firstname field is empty, hide state field
class RegisterUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        firstname = self.data.get('firstname') if self.is_bound else self.initial.get('firstname')
        lastname = self.data.get('lastname') if self.is_bound else self.initial.get('lastname')

        if not firstname and not lastname:
            print("RegisterUserForm: firstname or lastname is empty, hiding state field")
            self.fields['state'].widget = forms.HiddenInput()

    # specify the name of model to use
    class Meta:
        model = sj_users
        fields = [
            'firstname',
            'lastname',
            'byear',
            'gender',
            'email',
            'city',
            'state'
        ]

        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-floating mb-4 form-control form-control-lg',
                'required': True,
                }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),
            'byear': forms.NumberInput(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),
            'gender': forms.Select(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),
            'email': forms.EmailInput(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),
            'city': forms.TextInput(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),
            'state': forms.Select(attrs={
                'class': 'form-outline mb-4 form-control form-control-lg',
                'required': True,
                }),

        }

        labels = {
            'firstname': "Vorname *",
            'lastname': "Nachname *",
            'byear' : 'Jahrgang *',
            'gender' : 'Geschlecht *',
            'email' : 'E-Mail *',
            'city' : 'Ort *',
            'state' : 'An/Abmelden *',
        }

    def clean(self):
        cleaned_data = super().clean()

        firstname = cleaned_data.get('firstname')
        if firstname and not re.match(NAME_REGEX, firstname):
            self.add_error('firstname', "Im Vorname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt.")

        lastname = cleaned_data.get('lastname')
        if lastname and not re.match(NAME_REGEX, lastname):
            self.add_error('lastname', "Im Nachname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt.")

        # Gültige Jahrgänge (aktuelles Jahr minus maxAge)
        maxAge = 100

        byear = cleaned_data.get('byear')
        if byear not in range(date.today().year - maxAge, date.today().year):
            self.add_error('byear', f"Das Geburtsjahr muss zwischen {date.today().year - maxAge} und {date.today().year} liegen.")

        return cleaned_data        


# UserForm is used to update user data as logged in user
class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['city'].required = False

    # specify the name of model to use
    class Meta:
        model = sj_users
        fields = [
            'firstname',
            'lastname',
            'byear',
            'gender',
            'email',
            'city',
            'state'
        ]

        widgets = {
            'firstname': forms.TextInput(
                attrs={
                    'class': 'form-floating mb-4 form-control form-control-md',
                    'required': True,
                    'placeholder': 'Vorname *',
                }),
            'lastname': forms.TextInput(
                attrs={
                    'class': 'form-outline mb-4 form-control form-control-md',
                    'required': True,
                    'placeholder': 'Nachname *',
                }),
            'byear': forms.NumberInput(attrs={
                    'class': 'form-control form-control-md',
                    'required': True,
                }),
            'gender': forms.Select(attrs={
                    'class': 'form-control form-control-md',
                    'required': True,
                }),
            'email': forms.EmailInput(attrs={
                    'class': 'form-outline mb-4 form-control form-control-md',
                    'placeholder': 'E-Mail',
                }),
            'phone': forms.TextInput(attrs={
                    'class': 'form-outline mb-4 form-control form-control-md',
                }),
            'city': forms.TextInput(attrs={
                    'class': 'form-outline mb-4 form-control form-control-md',
                    'placeholder': 'Ort',
                }),
            'state': forms.Select(attrs={
                    'class': 'form-control form-control-md',
                    'required': True,
                }),

        }

        labels = {
            'firstname': "Vorname *",
            'lastname': "Nachname *",
            'byear' : 'Jahrgang *',
            'gender' : 'Geschlecht *',
            'email' : 'E-Mail',
            'phone' : 'Telefon',
            'city' : 'Ort',
            'state' : 'An/Abmelden *',
        }

    def clean(self):
        cleaned_data = super().clean()

        firstname = cleaned_data.get('firstname')
        if not re.match(NAME_REGEX, firstname):
            self.add_error('firstname', f"Im Vorname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt.")

        lastname = cleaned_data.get('lastname')
        if not re.match(NAME_REGEX, lastname):
            self.add_error('lastname', f"Im Nachname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt.")

        # Gültige Jahrgänge (aktuelles Jahr minus maxAge)
        maxAge = 100

        byear = cleaned_data.get('byear')
        if byear not in range(date.today().year-maxAge, date.today().year):
            error_message = f"Das Geburtsjahr muss zwischen {date.today().year - maxAge} und {date.today().year} liegen."
            self.add_error('byear', error_message)
        # Check if email is valid
        email = cleaned_data.get('email')
        if email and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            self.add_error('email', f"Bitte geben Sie eine gültige E-Mail-Adresse ein.")

        return cleaned_data
