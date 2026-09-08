import logging
logger = logging.getLogger('sj.logger')

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

# RegisterUserForm is used to register a new athlete via the web interface
# if lastname and firstname field is empty, hide state field
# if one of firstname, lastname, byear, gender is set, set these fields to readonly (diable) and show state field
class RegisterUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use self.instance (not self.data) so this is reliable on POST too: disabled
        # fields aren't submitted by the browser, so self.data would be empty for them.
        firstname = self.instance.firstname if self.instance.pk else None
        lastname = self.instance.lastname if self.instance.pk else None
        byear = self.instance.byear if self.instance.pk else None
        gender = self.instance.gender if self.instance.pk else None

        if not firstname and not lastname:
            logger.debug(f"RegisterUserForm (online reg): firstname or lastname is empty, hiding state field")
            self.fields['state'].widget = forms.HiddenInput()

        if firstname:
            self.fields['firstname'].disabled = True
        if lastname:
            self.fields['lastname'].disabled = True
        if byear:
            self.fields['byear'].disabled = True
        if gender:
            self.fields['gender'].disabled = True

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
                'class': 'form-outline mb-4 form-control form-control-lg',
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
"""
Logged in Member of group grp-admin are allowed to edit every field
all other users have restricted access
"""
class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Popped before super().__init__() - not a model field, only used to check group membership.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Use self.instance (not self.data) so this is reliable on POST too: disabled
        # fields aren't submitted by the browser, so self.data would be empty for them.
        firstname = self.instance.firstname if self.instance.pk else None
        lastname = self.instance.lastname if self.instance.pk else None
        byear = self.instance.byear if self.instance.pk else None
        gender = self.instance.gender if self.instance.pk else None
        logger.debug(f"UserForm: firstname={firstname}, lastname={lastname}, byear={byear}, gender={gender}")

        is_admin = bool(user) and user.groups.filter(name='grp-admin').exists()

        if not is_admin:
            # disabled=True is enforced server-side: submitted values are ignored and
            # the initial value is used instead (readonly widget attrs are not, and
            # have no effect on <select> widgets like gender).
            if firstname:
                self.fields['firstname'].disabled = True
            if lastname:
                self.fields['lastname'].disabled = True
            if byear:
                self.fields['byear'].disabled = True
            if gender:
                self.fields['gender'].disabled = True

            self.fields['startnum'].disabled = True

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
            'state',
            'startnum',
        ]

        widgets = {
            'firstname': forms.TextInput(
                attrs={
                    'class': 'form-outline form-control form-control-md',
                    'required': True,
                    'placeholder': 'Vorname *',
                }),
            'lastname': forms.TextInput(
                attrs={
                    'class': 'form-outline form-control form-control-md',
                    'required': True,
                    'placeholder': 'Nachname *',
                }),
            'byear': forms.NumberInput(attrs={
                    'class': 'form-outline form-control form-control-md',
                    'required': True,
                }),
            'gender': forms.Select(attrs={
                    'class': 'form-outline form-control form-control-md',
                    'required': True,
                }),
            'email': forms.EmailInput(attrs={
                    'class': 'form-outline form-control form-control-md',
                    'placeholder': 'E-Mail',
                }),
            'phone': forms.TextInput(attrs={
                    'class': 'form-outline form-control form-control-md',
                }),
            'city': forms.TextInput(attrs={
                    'class': 'form-outline form-control form-control-md',
                    'placeholder': 'Ort',
                }),
            'state': forms.Select(attrs={
                    'class': 'form-outline form-control form-control-md',
                    'required': True,
                }),
            'startnum': forms.NumberInput(attrs={
                    'class': 'form-outline form-control form-control-md bg-light text-muted',
                    'readonly': True,
                    'tabindex': '-1',
                    'style': 'user-select: none; pointer-events: none;',
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
            'startnum' : 'Startnummer',
        }

    def clean(self):
        cleaned_data = super().clean()

        firstname = cleaned_data.get('firstname')
        if not re.match(NAME_REGEX, firstname):
            firstname_error = f"Im Vorname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt."
            self.add_error('firstname', firstname_error)

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
