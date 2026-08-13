from django.contrib import admin
from .models import Contact, SMSLog

admin.site.register(Contact)
admin.site.register(SMSLog)