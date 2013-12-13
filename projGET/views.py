from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib import auth
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from projGET.forms import LoginForm, UserRegistrationForm
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm

def login(request):
	form = LoginForm()

	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('get:dashboard_page'))

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid(): # All validation rules pass
		    # Process the data in form.cleaned_data
		    # ...
			user = form.login()
			if user:
				auth.login(request, user)
				return HttpResponseRedirect(reverse('get:dashboard_page'))

	return render(request, 'login.html', {
	    'form': form,
	})

def invalid(request):
	return render_to_response('invalid_login.html')

def loggedout(request):
	auth.logout(request)
	return render_to_response('loggedout.html')

def register(request):
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('register_success'))
	args = {}
	args.update(csrf(request))
	args['form'] = UserRegistrationForm()
	return render_to_response('register.html', args)

def register_success(request):
	return render_to_response('register_success.html')
