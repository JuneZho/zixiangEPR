import xadmin

# Register your models here.

from .models import *


class EmployeeAdmin(object):
    list_display = ['nickname']
    search_fields = ['nickname']
    pass




class EmailVerifyRecordAdmin(object):
    pass

xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)