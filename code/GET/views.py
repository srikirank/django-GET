# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from GET.models import Contact, Person, Expense, Expense_Split, Group, Group_Contact, Group_Expense, Payment, Group_Payment
from GET.forms import AddContactForm, AddGroupForm, AddExpenseForm, AddGroupExpenseForm, AddPaymentForm, AddGroupPaymentForm, InviteForm
from datetime import datetime
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags


@login_required(login_url = reverse('login'))
def invite(request):
    if request.method == 'POST': # If the form has been submitted...
        form = InviteForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
			recipients = [form.cleaned_data.get('email')]
			html_content = "<body><h2>Welcome to GET!</h2><p>Click <a href='http://129.79.247.5:11000/register/'>here</a> to register!</p></body>"
			text_content = strip_tags(html_content)
			msg = EmailMultiAlternatives("GET Invitation", text_content, "GET Team", recipients)
			msg.attach_alternative(html_content, "text/html")
			msg.send()
			return HttpResponseRedirect(reverse('get:dashboard_page'))
    else:
        form = InviteForm() # An unbound form
    return render(request, 'GET/get_invite.html', {
        'form': form,
    })


@login_required(login_url = reverse('login'))
def loggedin(request):
	
	return render_to_response('GET/get_base.html', 
		{'first_name' : request.user.first_name})

@login_required(login_url = reverse('login'))
def contacts(request):
    context = {}
    context['contact_list'] = Contact.objects.filter(p_login__username = request.user.username)
    context['first_name'] = request.user.first_name
    return render_to_response('GET/get_contacts.html', context)

@login_required(login_url = reverse('login'))
def groups(request):
    context = {}
    user = Person.objects.get(username = request.user.username)
    group_contacts = user.gp_login.all()
    group_list = set([group_contact.group for group_contact in group_contacts])

    # own these people in a specific group
    group_contacts_iou = Group_Contact.objects.filter(p_login__username = request.user.username, iou__gt = 0).order_by('s_login')
    group_contacts_uoi = Group_Contact.objects.filter(s_login__username = request.user.username, iou__gt = 0)
    # participated such group activities
    involved_expense = []
    group_expenses = Group_Expense.objects.all().order_by('group')
    for group_expense in group_expenses:
    	for expense in group_expense.expense.expense_split_set.filter(login = request.user):
    		involved_expense.append(expense.expense)

    context['first_name'] = request.user.first_name
    context['group_list'] = group_list

    context['group_contacts_iou'] = group_contacts_iou
    context['group_contacts_uoi'] = group_contacts_uoi
    context['involved_expense'] = involved_expense
    context['no_group_own'] = len(group_contacts_iou) == 0
    context['no_own_group'] = len(group_contacts_uoi) == 0
    context['no_involved'] = len(involved_expense) == 0

    return render_to_response('GET/get_groups.html', context)

@login_required(login_url = reverse('login'))
def add_contact(request):
	form = AddContactForm(username = request.user.username)

	if request.method == 'POST':
		form = AddContactForm(request.POST,username = request.user.username)
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			p_login = Person.objects.get(username = request.user.username)
			s_login = Person.objects.get(email = form.cleaned_data.get('email'))
			iou = 0
			nick_name = form.cleaned_data.get('nick_name')
			c = Contact(p_login = p_login, s_login = s_login, iou = iou, nick_name = nick_name)

			# Add a hyperlink in Contacts page to change nickname
			c2 = Contact(p_login = s_login, s_login = p_login, iou = iou, nick_name = request.user.get_full_name())
			c.save()
			c2.save()
			##############
			####Send email
			subject = 'Added as a GET contact'
			message1 = "Hi " + s_login.first_name 
			message2 = "<p>%s added you as a contact on GET</p>" % (p_login.first_name)
			email = s_login.email

			html_content = "<body><h2>" + message1 + "</h2>" + message2 + "<p>Click <a href='http://129.79.247.5:11000/login/'>here</a> to login!</p></body>"
			text_content = strip_tags(html_content)
			msg = EmailMultiAlternatives(subject, text_content, "GET Team", [email])
			msg.attach_alternative(html_content, "text/html")
			msg.send()			
			##############

			return HttpResponseRedirect(reverse('get:contacts_page'))
	
	context = {}
	context['form'] = form
	context['first_name'] = request.user.first_name
	return render(request, 'GET/get_add_contact.html', context)

@login_required(login_url = reverse('login'))
def add_group(request):
	form = AddGroupForm(username = request.user.username)

	if request.method == 'POST':
		form = AddGroupForm(request.POST,username = request.user.username)
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			gname = form.cleaned_data.get('name')
			g = Group.objects.create(group_name = gname)
			contacts = form.cleaned_data.get('contacts')

			# Creating a list of members for the group
			members = [c.s_login for c in contacts]
			email_members = members			
			members.append(Person.objects.get(username = request.user.username))

			# Generating combinations of members for group contacts
			gcontacts = [(p,s) for p in members for s in members if p != s]
			
			for gcontact in gcontacts:
				Group_Contact.objects.create(p_login = gcontact[0], s_login = gcontact[1], group = g, iou = 0)
				if len(Contact.objects.filter(p_login__username = gcontact[0].username, s_login__username = gcontact[1].username)) == 0:
					Contact.objects.create(p_login = gcontact[0], s_login = gcontact[1], iou = 0, nick_name = gcontact[1].first_name)

			for member in email_members:
				##############
				####Send email
				p = Person.objects.get(username = request.user.username)
				subject = 'Added to a GET group'
				message = "Hi " + member.first_name + ",\n%s added you to '%s' group" % (p.first_name, g.group_name)
				email = member.email
				send_mail(subject, message, "GET Team", [email])
				##############				

			return HttpResponseRedirect(reverse('get:groups_page'))
	context = {}
	context['form'] = form
	context['first_name'] = request.user.first_name
	return render(request, 'GET/get_add_group.html', context)

@login_required(login_url = reverse('login'))
def dashboard(request):
	context = {}

	###################################################
	# this part for group
	###################################################
	contact_uoi = Contact.objects.filter(s_login = request.user, iou__gt = 0)
	contact_iou = Contact.objects.filter(p_login = request.user, iou__gt = 0)
	expenses = Expense.objects.filter(payer = request.user)
	all_expenses = Expense.objects.all().order_by('-exp_date')

	pay_list = []
	involve_list = []

	pay_total = 0;
	involved_total = 0;
	total_iou = 0;
	total_uoi = 0;
	# expenses in the last seven days
	expense_days = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
	# expenses in the last four weeks
	expense_weeks = {0:0, 1:0, 2:0, 3:0, 4:0}
	# expenses across the last year
	expense_months = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

	# expense as payer
	for expense in expenses:
		is_involved = len(expense.expense_split_set.filter(login = request.user)) != 0
		if is_involved:
			pay_total += expense.amount
			pay_list.append(expense)
	# expense as participant
	for expense in all_expenses:
		for entry in expense.expense_split_set.filter(login = request.user):
			involved_total += entry.expense.share

			diff_day = int((datetime.now().date() - entry.expense.exp_date).days)
			diff_month = int(datetime.now().date().month - entry.expense.exp_date.month)
			diff_year = int(datetime.now().date().year - entry.expense.exp_date.year)

			if diff_year == 0 and diff_day >= 0 and diff_day < 7:
				expense_days[diff_day] += entry.expense.share
			if diff_year == 0 and diff_day >= 0 and diff_day < 28:
				expense_weeks[diff_day / 7] += entry.expense.share
			if diff_year == 0 and diff_month >= 0 and diff_month <= 6:
				expense_months[diff_month] += entry.expense.share

			involve_list.append(entry.expense)

	# calculate total iou
	for i in contact_iou:
		total_iou += int(i.iou)
	# calculate total uoi
	for i in contact_uoi:
		total_uoi += int(i.iou)

	context['contact_uoi'] = contact_uoi
	context['contact_iou'] = contact_iou

	context['owe_no_one'] = len(contact_iou) == 0
	context['owed_by_none'] = len(contact_uoi) == 0

	context['first_name'] = request.user.first_name
	context['pay_list'] = pay_list
	context['involve_list'] = involve_list

	context['pay_total'] = pay_total
	context['involved_total'] = involved_total
	context['expense_days'] = expense_days
	context['expense_weeks'] = expense_weeks
	context['expense_months'] = expense_months


	###################################################
	# this part for payment
	###################################################
	ivolved_payment = Payment.objects.filter(payer_login = request.user).order_by('-pay_date')

	# payment for this week
	week_total_payment = 0
	payment_week = []
	# payment for this month
	month_total_payment = 0
	payment_month = []
	# payment across the whole year
	payment_months = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

	for payment in ivolved_payment:
		diff_day = int((datetime.now().date() - payment.pay_date).days)
		diff_month = int(datetime.now().date().month - payment.pay_date.month)
		diff_year = int(datetime.now().date().year - payment.pay_date.year)

		if diff_year == 0 and diff_day >= 0 and diff_day < 7:
			week_total_payment += payment.amount
			payment_week.append(payment)
		if diff_year == 0 and diff_month >= 0 and diff_month < 2:
			month_total_payment += payment.amount
			payment_month.append(payment)
		if diff_year == 0 and diff_month >= 0 and diff_month <= 6:
			payment_months[diff_month] += int(payment.amount)

	context['first_name'] = request.user.first_name
	context['not_made_payment'] = len(ivolved_payment) == 0
	context['week_total_payment'] = week_total_payment
	context['payment_week'] = payment_week
	context['month_total_payment'] = month_total_payment
	context['payment_month'] = payment_month
	context['payment_months'] = payment_months	

	###################################################
	# this part for group
	###################################################
	user = Person.objects.get(username = request.user.username)
	group_contacts = user.gp_login.all()
	group_list = set([group_contact.group for group_contact in group_contacts])

	# own these people in a specific group
	group_contacts_iou = Group_Contact.objects.filter(p_login__username = request.user.username, iou__gt = 0).order_by('s_login')
	group_contacts_uoi = Group_Contact.objects.filter(s_login__username = request.user.username, iou__gt = 0)

	context['first_name'] = request.user.first_name
	context['group_list'] = group_list

	for i in group_contacts_iou:
		total_iou += int(i.iou)
	for i in group_contacts_uoi:
		total_uoi += int(i.iou)

	context['group_contacts_iou'] = group_contacts_iou
	context['group_contacts_uoi'] = group_contacts_uoi
	context['no_group_own'] = len(group_contacts_iou) == 0
	context['no_own_group'] = len(group_contacts_uoi) == 0

	context['total_iou'] = total_iou
	context['total_uoi'] = total_uoi

	return render_to_response('GET/get_dashboard.html', context)

@login_required(login_url = reverse('login'))
def expenses(request):
	context = {}
	contact_uoi = Contact.objects.filter(s_login = request.user, iou__gt = 0)
	contact_iou = Contact.objects.filter(p_login = request.user, iou__gt = 0)
	expenses = Expense.objects.filter(payer = request.user)
	group_expense = Group_Expense.objects.all()
	all_expenses = Expense.objects.all().order_by('-exp_date')

	pay_list = []
	involve_list = []
	group_expense_id_list = [i.expense.id for i in group_expense]

	total_iou = 0;
	total_uoi = 0;

	# expense as payer
	for expense in expenses:
		is_involved = len(expense.expense_split_set.filter(login = request.user)) != 0
		if is_involved and expense.id not in group_expense_id_list:
			pay_list.append(expense)
	# expense as participant
	for expense in all_expenses:
		for entry in expense.expense_split_set.filter(login = request.user):
			if entry.expense.id not in group_expense_id_list:
				involve_list.append(entry.expense)

	# calculate total iou
	for i in contact_iou:
		total_iou += int(i.iou)
	# calculate total uoi
	for i in contact_uoi:
		total_uoi += int(i.iou)

	context['contact_uoi'] = contact_uoi
	context['contact_iou'] = contact_iou

	context['owe_no_one'] = len(contact_iou) == 0
	context['owed_by_none'] = len(contact_uoi) == 0

	context['first_name'] = request.user.first_name
	context['pay_list'] = pay_list
	context['involve_list'] = involve_list

	return render_to_response('GET/get_expenses.html', context)


@login_required(login_url = reverse('login'))
def add_expense(request):
	expenseform = AddExpenseForm(username = request.user.username)

	if request.method == 'POST':
		expenseform = AddExpenseForm(request.POST, username = request.user.username)
		if expenseform.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			amount = expenseform.cleaned_data.get('amount')
			description = expenseform.cleaned_data.get('description')
			exp_date = expenseform.cleaned_data.get('exp_date')
			split = expenseform.cleaned_data.get('split')

			payer = expenseform.cleaned_data.get('payer')
			count = len(split)

			expense = Expense.objects.create(description = description, amount = amount, exp_date = exp_date, payer = payer)

			# To update IOU of contacts
			split_cost = amount/count

			for person in split:
				es = Expense_Split(expense = expense, login = person)
				es.save()
				if person.username != payer.username:					
					c = Contact.objects.get(p_login__username = payer.username, s_login__username = person.username)
					c.iou -= split_cost
					c.iou = round(c.iou, 2)
					c.save()

					c = Contact.objects.get(p_login__username = person.username, s_login__username = payer.username)
					c.iou += split_cost
					c.iou = round(c.iou, 2)
					c.save()

					##############
					####Send email
					p = Person.objects.get(username = request.user.username)
					subject = 'An expense involving you was added'
					message = "Hi " + person.first_name + ",\n%s added an expense '%s' with you on %s-%s-%s." % (p.first_name, description, str(exp_date.month), str(exp_date.day), str(exp_date.year))
					email = person.email
					send_mail(subject, message, "GET Team", [email])
					##############								

			return HttpResponseRedirect(reverse('get:expenses_page'))

	context = {}
	context['form'] = expenseform
	context['first_name'] = request.user.first_name
	return render(request, 'GET/get_add_expense.html', context)

@login_required(login_url = reverse('login'))
def add_group_expense(request, g_id):
	g_name = Group.objects.get(id = g_id).group_name
	gexpenseform = AddGroupExpenseForm(username = request.user.username, id = g_id)
	
	if request.method == 'POST':
		gexpenseform = AddGroupExpenseForm(request.POST, username = request.user.username, id = g_id)
		if gexpenseform.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			amount = gexpenseform.cleaned_data.get('amount')
			description = gexpenseform.cleaned_data.get('description')
			exp_date = gexpenseform.cleaned_data.get('exp_date')
			split = gexpenseform.cleaned_data.get('split')
			payer = gexpenseform.cleaned_data.get('payer')

			count = len(split)

			expense = Expense.objects.create(description = description, amount = amount, exp_date = exp_date, payer = payer)
			gexpense = Group_Expense.objects.create(expense = expense, group = Group.objects.get(id = g_id))
			# To update IOU of contacts
			split_cost = amount/count

			for person in split:
				es = Expense_Split(expense = expense, login = person)
				es.save()
				if person.username != payer.username:
					c = Group_Contact.objects.get(p_login__username = payer.username, s_login__username = person.username, group__pk = g_id)
					c.iou -= split_cost
					c.iou = round(c.iou, 2)
					c.save()

					c = Group_Contact.objects.get(p_login__username = person.username, s_login__username = payer.username, group__pk = g_id)
					c.iou += split_cost
					c.iou = round(c.iou, 2)
					c.save()
					##############
					####Send email
					p = Person.objects.get(username = request.user.username)
					subject = "Added an expense in your Group - '%s'" % (g_name)
					message = "Hi " + person.first_name + ",\n%s added an expense '%s' in Group '%s' with you on %s-%s-%s." % (p.first_name, expense.description, g_name, str(exp_date.month), str(exp_date.day), str(exp_date.year))
					email = person.email
					send_mail(subject, message, "GET Team", [email])
					##############													

			return HttpResponseRedirect(reverse('get:expenses_page'))

	context = {}
	context['form'] = gexpenseform
	context['first_name'] = request.user.first_name
	context['g_name'] = g_name
	return render(request, 'GET/get_add_group_expense.html', context)

@login_required(login_url = reverse('login'))
def payment(request):
	context = {}
	ivolved_payment = Payment.objects.filter(payer_login = request.user).order_by('-pay_date')

	# payment for this week
	week_total_payment = 0
	payment_week = []
	# payment for this month
	month_total_payment = 0
	payment_month = []
	# payment across the whole year
	payment_months = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}

	for payment in ivolved_payment:
		diff_day = int((datetime.now().date() - payment.pay_date).days)
		diff_month = int(datetime.now().date().month - payment.pay_date.month)
		diff_year = int(datetime.now().date().year - payment.pay_date.year)

		if diff_year == 0 and diff_day >= 0 and diff_day < 7:
			week_total_payment += payment.amount
			payment_week.append(payment)
		if diff_year == 0 and diff_month >= 0 and diff_month < 2:
			month_total_payment += payment.amount
			payment_month.append(payment)
		if diff_year == 0 and diff_month >= 0 and diff_month <= 12:
			payment_months[diff_month] += int(payment.amount)

	context['first_name'] = request.user.first_name
	context['not_made_payment'] = len(ivolved_payment) == 0
	context['week_total_payment'] = week_total_payment
	context['payment_week'] = payment_week
	context['month_total_payment'] = month_total_payment
	context['payment_month'] = payment_month
	context['payment_months'] = payment_months

	return render_to_response('GET/get_payment.html', context)

@login_required(login_url = reverse('login'))
def add_payment(request):
	paymentform = AddPaymentForm(username = request.user.username)

	if request.method == 'POST':
		paymentform = AddPaymentForm(request.POST, username = request.user.username)
		if paymentform.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			amount = paymentform.cleaned_data.get('amount')
			description = paymentform.cleaned_data.get('description')
			pay_date = paymentform.cleaned_data.get('pay_date')
			payee = paymentform.cleaned_data.get('payee')
			payer = Person.objects.get(username = request.user.username)

			p = Payment.objects.create(description = description, amount = amount, pay_date = pay_date, payer_login = payer, payee_login = payee)

			# To update IOU of contacts
			c = Contact.objects.get(p_login__username = payer.username, s_login__username = payee.username)
			c.iou -= amount
			c.iou = round(c.iou, 2)
			c.save()

			c = Contact.objects.get(p_login__username = payee.username, s_login__username = payer.username)
			c.iou += amount
			c.iou = round(c.iou, 2)
			c.save()

			##############
			####Send email
			p = Person.objects.get(username = request.user.username)
			subject = 'Recorded a payment made to you'
			message = "Hi " + payee.first_name + ",\n%s recorded a payment '%s' with you on %s-%s-%s." % (p.first_name, description, str(pay_date.month), str(pay_date.day), str(pay_date.year))
			email = payee.email
			send_mail(subject, message, "GET Team", [email])
			##############											
			return HttpResponseRedirect(reverse('get:payments_page'))

	context = {}
	context['form'] = paymentform
	context['first_name'] = request.user.first_name
	return render(request, 'GET/get_add_payment.html', context)

@login_required(login_url = reverse('login'))
def add_group_payment(request, g_id):
	g_name = Group.objects.get(id = g_id).group_name
	gpaymentform = AddGroupPaymentForm(username = request.user.username, id = g_id)
	
	if request.method == 'POST':
		gpaymentform = AddGroupPaymentForm(request.POST, username = request.user.username, id = g_id)
		if gpaymentform.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			amount = gpaymentform.cleaned_data.get('amount')
			description = gpaymentform.cleaned_data.get('description')
			pay_date = gpaymentform.cleaned_data.get('pay_date')
			payee = gpaymentform.cleaned_data.get('payee')
			payer = Person.objects.get(username = request.user.username)

			payment = Payment.objects.create(description = description, amount = amount, pay_date = pay_date, payer_login = payer, payee_login = payee)
			gpayment = Group_Payment.objects.create(payment = payment, group = Group.objects.get(id = g_id))			
			# To update IOU of contacts
			c = Group_Contact.objects.get(p_login__username = payer.username, s_login__username = payee.username, group__pk = g_id)
			c.iou -= amount
			c.iou = round(c.iou, 2)
			c.save()

			c = Group_Contact.objects.get(p_login__username = payee.username, s_login__username = payer.username, group__pk = g_id)
			c.iou += amount
			c.iou = round(c.iou, 2)
			c.save()
			##############
			####Send email
			p = Person.objects.get(username = request.user.username)
			subject = 'Recorded a payment in your group'
			message = "Hi " + payee.first_name + ",\n%s recorded a payment '%s' in Group '%s' with you on %s-%s-%s." % (p.first_name, description, g_name ,str(pay_date.month), str(pay_date.day), str(pay_date.year))
			email = payee.email
			send_mail(subject, message, "GET Team", [email])
			##############														
			return HttpResponseRedirect(reverse('get:payments_page'))

	context = {}
	context['form'] = gpaymentform
	context['g_name'] = g_name
	context['first_name'] = request.user.first_name
	return render(request, 'GET/get_add_group_payment.html', context)