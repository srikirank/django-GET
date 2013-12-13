from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Person(User):
	def __unicode__(self):
		return self.first_name 
	
	class Meta:
		proxy = True

class Group(models.Model):
	group_name = models.CharField(max_length = 15)

	def __unicode__(self):
		return self.group_name

class Contact(models.Model):
	"""Relation to store contacts"""
	p_login = models.ForeignKey('Person', related_name = 'p_login')
	s_login = models.ForeignKey('Person', related_name = 's_login')
	iou = models.DecimalField(max_digits = 10, decimal_places = 2)

	# To-be-Fixed: null values for nick_name aren't being accepted using QuerySet API
	nick_name = models.CharField(max_length = 50, null = True, blank = True)

	# def __unicode__(self):
	# 	return str(self.p_login.first_name) + "---->" +str(self.s_login.first_name) + "____" + str(self.iou)

	def __unicode__(self):
		return str(self.s_login.first_name)

	class Meta():
		ordering = ('p_login',)
		unique_together = ('p_login', 's_login')		

	# """Business Logic: Ensuring that (p_login, s_login) combination is unique."""
	# # def save(self, *args, **kwargs):
	# # 	from django.core.exceptions import ObjectDoesNotExist
	# # 	try:
	# # 		p = Contact.objects.get(p_login__username = self.p_login.username, s_login__username = self.s_login.username)
	# # 		print("\nContact already exists!\nObject not saved\n")
	# # 	except ObjectDoesNotExist:
	# # 		super(Contact, self).save(*args, **kwargs)


class Group_Contact(models.Model):
	"""Relation to store Group Contacts."""
	p_login = models.ForeignKey('Person', related_name = 'gp_login')
	s_login = models.ForeignKey('Person', related_name = 'gs_login')
	group = models.ForeignKey('Group', related_name = 'group_contact')
	iou = models.DecimalField(max_digits = 10, decimal_places = 2)

	# def __unicode__(self):
	# 	return str(self.p_login) + " --> " + str(self.s_login) + " --> " + str(self.iou)

	def __unicode__(self):
		return str(self.p_login)

	class Meta():
		ordering = ('p_login',)
		unique_together = ('p_login', 's_login', 'group')

class Invite(models.Model):
	"""To capture the emails of the invites sent."""
	email = models.EmailField(primary_key = True)

	def save(self, *args, **kwargs):
		from django.core.exceptions import ObjectDoesNotExist
		try:
			p = Invites.objects.get(email = self.email)
			print("\nInvite Email already sent!\nObject not saved\n")
		except ObjectDoesNotExist:
			super(Invites, self).save(*args, **kwargs)

class Expense(models.Model):
	"""docstring for Expense"""
	description = models.CharField(max_length = 50)
	exp_date = models.DateField()
	amount = models.DecimalField(max_digits = 10, decimal_places = 2)
	payer = models.ForeignKey('Person')

	def __unicode__(self):
		return str(self.exp_date.month) + "/ " + str(self.exp_date.day) + "/ " + str(self.exp_date.year) + " - " + self.description + " : " + str(self.amount)

	def calculate_share(self):
		count = len(self.expense_split_set.all())
		share = round(self.amount / count, 2)
		return share

	share = property(calculate_share)

class Group_Expense(models.Model):
	expense = models.ForeignKey('Expense')
	group = models.ForeignKey('Group')

	def __unicode__(self):
		return str(self.group.id) + " - " + str(self.expense)

class Expense_Split(models.Model):
	"""Expense splitting among people. To be fixed for variable amounts"""
	expense = models.ForeignKey('Expense')
	login = models.ForeignKey('Person')

	def __unicode__(self):
		return str(self.login) + " - " + str(self.expense)


class Payment(models.Model):
	description = models.CharField(max_length = 50)
	pay_date = models.DateField()

	# Payer - Who makes the payment
	# Payee - Who receives the payment
	payer_login = models.ForeignKey('Person', related_name = 'payer_login')
	payee_login = models.ForeignKey('Person', related_name = 'payee_login')
	amount = models.DecimalField(max_digits = 10, decimal_places = 2)

	def __unicode__(self):
		return str(self.pay_date.month) + "/ " + str(self.pay_date.day) + "/ " + str(self.pay_date.year) + " - " + self.description + " : " + str(self.amount)

class Group_Payment(models.Model):
	payment = models.ForeignKey('Payment')
	group = models.ForeignKey('Group')

	def __unicode__(self):
		return str(self.group.id) + " - " + str(self.payment)
