import xadmin

# Register your models here.


from .models import *


class ProjectAdmin(object):
    change_form_template = 'xadmin/change_form.html'

    def save_models(self):
        obj = self.new_obj
        obj.save()




    def setup_forms(self):
        """
        配置 Form。
        """
        print("changing view")
        todo = ContentType.objects.get(app_label='basedata', model='todolist')
        todo_list = todo.model_class().objects.filter(user=self.request.user)

        if todo_list.count() > 0:
            print('we fount it')
            change_form_template = 'xadmin/change_form.html'
            can_restart = True
            unread = todo_list.filter(is_read=0)
            show_workflow_line = True
            if unread.count() > 0:
                import datetime
                unread.update(is_read=1, read_time=datetime.datetime.now())

        helper = self.get_form_helper()
        if helper:
            self.form_obj.helper = helper





xadmin.site.register(Project,ProjectAdmin)


class OutsourceAdmin(object):
    pass


xadmin.site.register(Outsource,OutsourceAdmin)


class deviceChangeAdmin(object):
    pass


xadmin.site.register(Device_change,deviceChangeAdmin)



class Outsource_itemsAdmin(object):
    pass


xadmin.site.register(Outsource_items,Outsource_itemsAdmin)


class DeviceRecord(object):
    pass


xadmin.site.register(Device,DeviceRecord)



class Material_useAdmin(object):
    pass


xadmin.site.register(Material_use,Material_useAdmin)


class Device_finalAdmin(object):
    pass


xadmin.site.register(Device_final,Device_finalAdmin)



class Finish_reportAdmin(object):
    pass


xadmin.site.register(Finish_report,Finish_reportAdmin)


class work_hourAdmin(object):
    pass


xadmin.site.register(work_hour,work_hourAdmin)


class feedback_reportAdmin(object):
    pass


xadmin.site.register(feedback_report,feedback_reportAdmin)


class HistoryAdmin(object):
    pass


xadmin.site.register(History, HistoryAdmin)


class TodoListAdmin(object):
    list_display = ['code', 'project', 'is_read', 'status', 'arrived_time']
    list_filter = ['status','user']

    def queryset(self):
        qs = super(TodoListAdmin, self).queryset()
        if self.request.user.is_superuser:  # 超级用户可查看所有数据
            return qs
        else:
            return qs.filter(user=self.request.user)  # user是IDC Model的user字段



xadmin.site.register(TodoList, TodoListAdmin)

