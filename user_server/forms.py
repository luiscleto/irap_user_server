from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from user_server.models import *


class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. Please try another one."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data


class ExperimentForm(forms.Form):
    title = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=60)), label=_("Title"), error_messages={ 'invalid': _("This value must contain only up to 60 letters, numbers and underscores.") })
    description = forms.CharField(max_length=1500, widget=forms.Textarea)

    def clean_title(self):
        try:
            exp = Experiment.objects.get(title__iexact=self.cleaned_data['title'])
        except Experiment.DoesNotExist:
            return self.cleaned_data['title']
        raise forms.ValidationError(_("There is already an experiment with that title. Please choose a new one."))

    def clean_description(self):
        return self.cleaned_data['description']


class ReferenceGenomeForm(forms.Form):
    species = forms.RegexField(regex=r'^[a-zA-Z\s]+$', widget=forms.TextInput(attrs=dict(required=True, max_length=80, min_length=8)), label=_("Species"), error_messages={'invalid': _("This value must contain between 8 and 80 letters.")})

    def clean_species(self):
        return self.cleaned_data['species']
