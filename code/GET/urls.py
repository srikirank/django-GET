from django.conf.urls import patterns, url
from django.contrib import admin
# from GET.views import ContactView

urlpatterns = patterns('GET.views',
    # url(r'^home/$','loggedin', name = 'home_page'),
    ## Home
    url(r'^home/$', 'dashboard', name = 'dashboard_page'),
    url(r'^invite/$', 'invite', name = 'invite_page'),    
    ## Contacts
    url(r'^contacts/$','contacts', name = 'contacts_page'),
    url(r'^contacts/add/$', 'add_contact', name = 'add_contact_page'),
    ##
    ## Groups
    ##
    url(r'^groups/$', 'groups', name = 'groups_page'),
    url(r'^groups/add/$', 'add_group', name = 'add_group_page'),
    ##
    ## Expenses
    ##
    url(r'^expenses/$', 'expenses', name = 'expenses_page'),
    url(r'^expenses/add/$', 'add_expense', name = 'add_expense_page'),
    url(r'^groups/(?P<g_id>\d+)/expense/$', 'add_group_expense', name = 'add_group_expense_page'),
    ##
    ## Payments
    ##
    url(r'^payments/$', 'payment', name = 'payments_page'),
    url(r'^payments/add/$', 'add_payment', name = 'add_payment_page'),
    url(r'^groups/(?P<g_id>\d+)/payment/$', 'add_group_payment', name = 'add_group_payment_page'),
)