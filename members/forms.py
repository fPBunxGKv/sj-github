from django import forms
from .models import sj_users,sj_results
from django.core.exceptions import ValidationError
import re
from datetime import date


class ResultForm(forms.ModelForm):
    class Meta:
        model = sj_results
        fields = [
            'fk_sj_users', 'fk_sj_events', 'run_nr', 'line_nr', 'result', 'result_category', 'state'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

    def clean(self):
        #data = self.cleaned_data
        cleaned_data = super().clean()
        return cleaned_data

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

        # # Prüfen, ob Vor- und Nachname Buchstaben enthalten
        # NAME_REGEX = "^[a-zA-ZäöüÄÖÜßéàè]+(?:[- ][a-zA-ZäöüÄÖÜßéàè]+)*$"
        
        # firstname = cleaned_data.get('firstname')
        # if not re.match(NAME_REGEX, firstname):
        #     self._errors['firstname'] = self.error_class(["Im Vorname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt."])

        # lastname = cleaned_data.get('lastname')
        # if not re.match(NAME_REGEX, lastname):
        #     self._errors['lastname'] = self.error_class(["Im Nachname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt."])
        
        # # Gültige Jahrgänge (aktuelles Jahr minus maxAge)
        # maxAge = 100

        # byear = cleaned_data.get('byear')
        # if byear not in range(date.today().year-maxAge, date.today().year):
        #     self._errors['byear'] = self.error_class(["Das Geburtsjahr muss zwischen " + str(date.today().year-maxAge) + " und " +str(date.today().year) + " liegen."])
        
        return cleaned_data

# create a ModelForm
class RegisterUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
    
    # specify the name of model to use
    class Meta:
        model = sj_users
        fields = [
            'firstname', 'lastname', 'byear', 'gender', 'email', 'phone', 'city', 'state'
        ]
        
        widgets = {
            'firstname': forms.TextInput(attrs={
                # 'class': 'form-outline',
                # 'class': 'form-control form-control-lg',
                'required': True,
                }),
            'lastname': forms.TextInput(attrs={
                # 'class': 'form-outline',
                # 'class': 'form-control form-control-lg',
                'required': True,
                }),
            'byear': forms.NumberInput(attrs={
                # 'class': 'form-control',
                'required': True,
                }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                }),
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
            'state': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                }),

        }

        labels = {
            'firstname': "Vorname *",
            'lastname': "Nachname *",
            'byear' : 'Jahrgang *',
            'gender' : 'Geschlecht *',
            'email' : 'E-Mail *',
            'phone' : 'Telefon',
            'city' : 'Ort *',
            'state' : 'An/Abmelden *',
        }
    def clean(self):
        #data = self.cleaned_data
        cleaned_data = super().clean()

        # Prüfen, ob Vor- und Nachname Buchstaben enthalten
        NAME_REGEX = "^[a-zA-ZäöüÄÖÜßéàè]+(?:[- ][a-zA-ZäöüÄÖÜßéàè]+)*$"
        
        firstname = cleaned_data.get('firstname')
        if not re.match(NAME_REGEX, firstname):
            self._errors['firstname'] = self.error_class(["Im Vorname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt."])

        lastname = cleaned_data.get('lastname')
        if not re.match(NAME_REGEX, lastname):
            self._errors['lastname'] = self.error_class(["Im Nachname sind nur Buchstaben, Bindestriche und Leerzeichen erlaubt."])
        
        # Gültige Jahrgänge (aktuelles Jahr minus maxAge)
        maxAge = 100

        byear = cleaned_data.get('byear')
        if byear not in range(date.today().year-maxAge, date.today().year):
            self._errors['byear'] = self.error_class(["Das Geburtsjahr muss zwischen " + str(date.today().year-maxAge) + " und " +str(date.today().year) + " liegen."])
        
        return cleaned_data



