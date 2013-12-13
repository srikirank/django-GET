from django.contrib import admin
from GET.models import Person
from GET.models import Group
from GET.models import Contact
from GET.models import Group_Contact
from GET.models import Invite
from GET.models import Expense
from GET.models import Group_Expense
from GET.models import Expense_Split
from GET.models import Payment
from GET.models import Group_Payment

admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Contact)
admin.site.register(Group_Contact)
admin.site.register(Invite)
admin.site.register(Expense)
admin.site.register(Group_Expense)
admin.site.register(Expense_Split)
admin.site.register(Payment)
admin.site.register(Group_Payment)