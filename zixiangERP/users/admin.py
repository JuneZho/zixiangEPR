from django.contrib import admin

# Register your models here.

from .models import *


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['nickname']
    search_fields = ['nickname']
    pass


admin.site.register(Employee,EmployeeAdmin)

class EmailVerifyRecordAdmin(admin.ModelAdmin):
    pass


admin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)