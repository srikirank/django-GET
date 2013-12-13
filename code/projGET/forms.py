from django.contrib import auth
from django import forms
from django.core.urlresolvers import reverse
from django.forms import Form, ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Button, Hidden
from crispy_forms.bootstrap import FormActions, AppendedText


class UserRegistrationForm(UserCreationForm):
	email = forms.EmailField(required = True)
	first_name = forms.CharField(required=True, label="First Name")
	last_name = forms.CharField(required=True, label="Last Name")
	helper = FormHelper()
	helper.form_id = 'register_form'
        #helper.form_action = reverse('register')
        helper.form_method = 'post'
        helper.layout = Layout(
        Fieldset("Welcome! Fill the form below to Register", 'first_name', 'last_name','username', 'email', 'password1', 'password2',),
          FormActions(Submit('submit', 'Register'),Button('cancel', 'Cancel')),)
          
	class Meta:
		model = User
		fields = ('first_name', 'last_name','username', 'password1', 'password2')
		
	def save(self, commit=True):
		user = super(UserRegistrationForm, self).save(commit=False)
		user.email = self.cleaned_data['email']	
		user.first_name = self.cleaned_data['first_name']	
		user.last_name = self.cleaned_data['last_name']	
		
		if commit:
			user.save()	
		return user

class LoginForm(Form):
	username = forms.CharField(required = True)
	password = forms.CharField(required = True, widget = forms.PasswordInput())

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = '/login/'

		self.helper.add_input(Submit('submit', 'Submit'))

	def clean(self):
		cleaned_data = super(LoginForm, self).clean()
		username = cleaned_data.get('username', None)
		password = cleaned_data.get('password', None)
		user = auth.authenticate(username = username, password = password)

		if not user or not user.is_active:
			raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
		return cleaned_data

	def login(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		user = auth.authenticate(username=username, password=password)
		return user
