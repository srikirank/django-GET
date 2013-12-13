from django import forms
from GET.models import Person, Contact
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Button, Hidden
from crispy_forms.bootstrap import FormActions, AppendedText

class InviteForm(forms.Form):
	email = forms.EmailField(required = True, label = "Enter Email Address:")
	helper = FormHelper()
	helper.form_id = 'invite_form'
	helper.form_method = 'post'
	helper.layout = Layout(
			Fieldset(
				"Send Invite",
				'email',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				),)
	
class AddContactForm(forms.Form):
	email = forms.EmailField(required = True)
	nick_name = forms.CharField(required = False)
	username = forms.CharField(required = False)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		super(AddContactForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('get:add_contact_page')
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_id = 'add_contact_form'
		self.helper.layout = Layout(
			Fieldset(
				'Add Contact:',
				'email',
				'nick_name',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				),
			Field('username',type = "hidden"),
			Hidden('username',username),
			)

		# self.helper.add_input(Submit('submit', 'Submit'))

	def clean(self):
		cleaned_data = super(AddContactForm, self).clean()
		email = cleaned_data.get('email', None)
		nick_name = cleaned_data.get('nick_name', None)
		username = cleaned_data.get('username', None)

		user = Person.objects.filter(email = email)

		"""Business Logic: Ensuring that user already exits."""
		if not user:
			raise forms.ValidationError("Could not find the person. You can only add an existing user.")
		
		"""Business Logic: Ensuring that (p_login, s_login) combination is unique."""
		from django.core.exceptions import ObjectDoesNotExist
		try:
			c = Contact.objects.get(p_login__username = username, s_login = user[0])
			print("\nContact already exists!\nObject not saved\n")
			raise forms.ValidationError("Contact already exists.")
		except ObjectDoesNotExist:
			pass
		return cleaned_data


class AddGroupForm(forms.Form):
	name = forms.CharField(
		required = True,
		label = 'Give it a name:')

	contacts = forms.ModelMultipleChoiceField(
		label = 'Add them',
		queryset = Person.objects.none(),
		widget = forms.CheckboxSelectMultiple(),
		required = True,)

	username = forms.CharField(required = False)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		super(AddGroupForm, self).__init__(*args, **kwargs)
		self.fields['contacts'].queryset = Person.objects.get(username = username).p_login.all()
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_id = 'add_group_form'
		self.helper.form_action = reverse('get:add_group_page')
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.layout = Layout(
			Fieldset(
				'Create a Group:',
				'name',
				'contacts',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				),
			)

class AddExpenseForm(forms.Form):
	amount = forms.DecimalField(
		max_digits = 10, 
		decimal_places = 2,
		required = True,
		label = 'Amount'
		)

	description = forms.CharField(
		required = True,
		label = 'Description')

	exp_date = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'id':'datepicker',
                                }),
		required = True,
		label = 'Date',		
		)

	payer = forms.ModelChoiceField(
		label = 'Who paid?',
		queryset = Person.objects.none(),
		required = True,
		)

	split = forms.ModelMultipleChoiceField(
		label = 'Who all?',
		queryset = Person.objects.none(),
		widget = forms.CheckboxSelectMultiple(),
		required = True,
		)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		super(AddExpenseForm, self).__init__(*args, **kwargs)
		person_ids = [contact.s_login.id for contact in Person.objects.get(username = username).p_login.all()]
		person_ids.append(Person.objects.get(username = username).id)
		
		split = Person.objects.filter(pk__in = person_ids)

		self.fields['split'].queryset = split
		self.fields['payer'].queryset = split

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('get:add_expense_page')
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_id = 'add_expense_form'
		self.helper.layout = Layout(
			Fieldset(
				'Add an expense:',
				AppendedText('amount', '$'),
				'description',
				'exp_date',
				'payer',
				'split',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				)
			)

	def clean(self):
		cleaned_data = super(AddExpenseForm, self).clean()
		split = cleaned_data.get('split')
		payer = cleaned_data.get('payer', None)

		# contacts = [(p,s) for p in split for s in split if p != s]
		## To be part of an expense, the involved people should be in Contacts table.
		from django.core.exceptions import ObjectDoesNotExist
		for person in split:
			if person != payer:			
				try:
					c = Contact.objects.get(p_login__username = payer.username, s_login__username = person.username)
				except ObjectDoesNotExist:
					raise forms.ValidationError("Since %s is paying, add only related people in the expense." % payer.first_name.upper())
		return cleaned_data

class AddGroupExpenseForm(forms.Form):
	amount = forms.DecimalField(
		max_digits = 10, 
		decimal_places = 2,
		required = True,
		label = 'Amount'
		)

	description = forms.CharField(
		required = True,
		label = 'Description')

	exp_date = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'id':'datepicker',
                                }),
		required = True,
		label = 'Date',
		)

	payer = forms.ModelChoiceField(
		label = 'Who paid?',
		queryset = Person.objects.none(),
		required = True,
		)

	split = forms.ModelMultipleChoiceField(
		label = 'Who all?',
		queryset = Person.objects.none(),
		widget = forms.CheckboxSelectMultiple(),
		required = True,
		)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		id = kwargs.pop('id', None)

		super(AddGroupExpenseForm, self).__init__(*args, **kwargs)

		person_ids = [contact.s_login.id for contact in Person.objects.get(username = username).gp_login.filter(group__pk = id)]
		person_ids.append(Person.objects.get(username = username).id)
		
		split = Person.objects.filter(pk__in = person_ids)

		self.fields['split'].queryset = split
		self.fields['payer'].queryset = split

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('get:add_group_expense_page', args = (id, ))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_id = 'add_group_expense_form'
		self.helper.layout = Layout(
			Fieldset(
				'Add an expense:',
				AppendedText('amount', '$'),
				'description',
				'exp_date',
				'payer',
				'split',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				)
			)

class AddPaymentForm(forms.Form):
	amount = forms.DecimalField(
		max_digits = 10, 
		decimal_places = 2,
		required = True,
		label = 'Amount'
		)

	description = forms.CharField(
		required = True,
		label = 'Description')

	pay_date = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'id':'datepicker',
                                }),
		required = True,
		label = 'Date',
		)

	payee = forms.ModelChoiceField(
		label = 'Whom?',
		queryset = Person.objects.none(),
		required = True,
		)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		super(AddPaymentForm, self).__init__(*args, **kwargs)
		person_ids = [contact.s_login.id for contact in Person.objects.get(username = username).p_login.all()]
		
		payee = Person.objects.filter(pk__in = person_ids)

		self.fields['payee'].queryset = payee

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('get:add_payment_page')
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_id = 'add_payment_form'
		self.helper.layout = Layout(
			Fieldset(
				'Add an payment:',
				AppendedText('amount', '$'),
				'description',
				'pay_date',
				'payee',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				)
			)

class AddGroupPaymentForm(forms.Form):
	amount = forms.DecimalField(
		max_digits = 10, 
		decimal_places = 2,
		required = True,
		label = 'Amount'
		)

	description = forms.CharField(
		required = True,
		label = 'Description')

	pay_date = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'id':'datepicker',
                                }),
		required = True,
		label = 'Date',
		)

	payee = forms.ModelChoiceField(
		label = 'Whom?',
		queryset = Person.objects.none(),
		required = True,
		)

	def __init__(self, *args, **kwargs):
		username = kwargs.pop('username', None)
		id = kwargs.pop('id', None)
		
		super(AddGroupPaymentForm, self).__init__(*args, **kwargs)
		person_ids = [contact.s_login.id for contact in Person.objects.get(username = username).gp_login.filter(group__pk = id)]
		
		payee = Person.objects.filter(pk__in = person_ids)

		self.fields['payee'].queryset = payee

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('get:add_group_payment_page', args = (id, ))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_id = 'add_group_payment_form'
		self.helper.layout = Layout(
			Fieldset(
				'Add an payment:',
				AppendedText('amount', '$'),
				'description',
				'pay_date',
				'payee',
				),
			FormActions(
				Submit('submit', 'Add'),
				Button('cancel', 'Cancel')
				)
			)