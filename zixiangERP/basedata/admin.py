
# coding = utf-8
from django.contrib import admin
from basedata import models as mymodels
from zixiangERP import view
from django.contrib import messages
from django.db import models
from django.http import HttpResponseRedirect

from users import models as user_models



# Register your models here.
from django.contrib.admin.templatetags.admin_modify import register, submit_row as original_submit_row

@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    ''' submit buttons context change '''
    ctx = original_submit_row(context)
    ctx.update({
    'show_save_and_add_another': context.get('show_save_and_add_another',
                                             ctx['show_save_and_add_another']),
    'show_save_and_continue': context.get('show_save_and_continue',
                                          ctx['show_save_and_continue']),
    'show_save': context.get('show_save',
                             ctx['show_save']),
    'show_delete_link': context.get('show_delete_link', ctx['show_delete_link'])
    })
    return ctx

from .models import *
ROLES = ('普通员工','总经理',
             '商务经理',
             '财务经理',
             '工程经理',
             '技术经理',
             '库管','营销经理','行政经理')
WORK_FLOW_NODE = ((0, u"合同签约人填写"),
        (1, u"商务部审批并填写设备信息"),
        (2, u"财务审批"),
        (3, u"营销经理审批"),
        (4, u"总经理审批"),
        (5, u"工程经理经理指派项目经理",),
        (6, u"项目经理施工"),
        (7, u"工程经理审批"),
        (8, u"技术经理审批"),
        (9, u"总经理审批"),
        (10, u"完成"),
        (11, u"商务部反对，暂挂"),
        (12, u"财务反对，暂挂"),
        (13, u"营销经理反对，暂挂"),
        (14, u"总经理，暂挂"),
        (15, u"暂挂"),
        (16, u"暂挂"),
        (17, u"工程经理反对，暂挂"),
        (18, u"技术经理反对，暂挂"),
        (19, u"总经理反对，暂挂"),
        (20, u"终止"))
FLOW_ROLES = ((0, u"合同签约人"),
    (1, u"商务经理"),
    (2, u"财务经理"),
    (3, u"营销经理"),
    (4, u"总经理"),
    (5, u"工程经理"),
    (6, u"项目经理"),
    (7, u"工程经理"),
    (8, u"技术经理"),
    (9, u"总经理"))
class tmp:
    proID = 0

    def setID(self,ID):
        self.proID = ID

    def getID(self):
        return self.proID

class ProjectAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if request.user.title ==4:

            return ['active','begin','starter','name','cusname',
                    'cusaddr','recname','recaddr','receiver',
                    'receiverdep','receiverphone','receivertele',
                    'payer','payerdep','payerphone','payertele','total_price','kaipiao',
                    'description','associated_file','total_hour','total_mat','total_money','niehe_hour','workflow_node','end']

        elif request.user == obj.manager:
            return ['active', 'begin', 'starter', 'name', 'cusname',
                    'cusaddr', 'recname', 'recaddr', 'receiver',
                    'receiverdep', 'receiverphone', 'receivertele',
                    'payer', 'payerdep', 'payerphone', 'payertele', 'total_price', 'kaipiao',
                    'description', 'associated_file', 'total_hour', 'total_mat', 'total_money','workflow_node','end']
        else:
            return ['workflow_node', 'end', 'total_price', 'manager', 'active', 'niehe_hour', 'total_hour', 'total_mat',
                    'total_money']

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """

        :param request:
        :param object_id:
        :param form_url:
        :param extra_context:
        :return:
        """
        show_save = True
        show_workflow_line = False
        can_restart = False
        can_edit = False
        show_submit_button = False
        project_id = None
        # print app_info
        try:
            project_id = (str(request).split("project/")[1].split("/")[0])
            tmp.proID = project_id
            pro = Project.objects.get(id=project_id)
            todo = TodoList.objects.filter(user=request.user,project = pro)
            his = History.objects.filter(user=request.user,project = pro)
            print(his.count())
            if todo.count() > 0 or his.count() > 0:
                unread = todo.filter(is_read=0)
                show_workflow_line = True
                if unread.count() > 0:
                    import datetime
                    unread.update(is_read=1, read_time=datetime.datetime.now())
                if pro.workflow_node >= 10 and request.user == pro.starter:
                    can_restart = True
                    show_workflow_line = True
                if pro.workflow_node == 9:
                    show_save = False

        except Exception as e:
                print(e)  # is add
                show_workflow_line = False


        # print extra_context
        extra_context = extra_context or {}
        ctx = dict(
            show_workflow_line=show_workflow_line,
            can_restart=can_restart,
            can_edit=can_edit,
            show_submit_button=show_submit_button,
            project_id=project_id,
            show_save_and_add_another = False,
            show_delete_link =True,
            show_save = show_save
        )

        extra_context.update(ctx)
        return super(ProjectAdmin, self).changeform_view(request, object_id, form_url, extra_context)


    def save_model(self, request, obj, form, change):

        msg = ''
        if change:

            if request.user.title == 4:
                '''工程经理'''
                if obj.manager == None:
                    msg += "未指派项目经理,修改失败"
                else:
                    msg += "您的更改生效了"
                    obj.save()

            elif request.user == obj.manager:
                dict = ('竣工报告','项目经理自评','设备更改','设备最终','工时记录','材料领取')
                try:
                    result = [Finish_report.objects.get(project_info=obj).agreed,feedback_report.objects.get(project_info=obj).agreed,
                         Device_change.objects.get(project_info=obj).agreed,
                         Device_final.objects.get(project_info=obj).agreed,
                         work_hour.objects.get(project_info=obj).agreed,
                         Material_use.objects.get(project_info=obj).agreed]
                except Exception as e:
                    self.message_user(request,"信息不全，无法提交")
                    return
                if False in result:

                    self.message_user(request,'分流程: '+dict[result.index(False)]+' 未完成审批，无法提交')
                    return

                else:
                    obj.save()
            elif request.user == obj.starter:
                msg += "您的更改生效了"
                obj.save()

            todo = ContentType.objects.get(app_label='basedata', model='todolist')
            todo_list = todo.model_class().objects.filter(user=request.user,project=obj)
            if obj.workflow_node ==0:
                curuser = obj.starter
            else:
                if FLOW_ROLES[obj.workflow_node][1] == '项目经理':
                    self.message_user(request, '当前节点项目经理,您无权审批')
                    return
                curuser = user_models.Employee.objects.get(title=ROLES.index(FLOW_ROLES[obj.workflow_node][1]))

            if "_next" in request.POST:
                if todo_list.count() > 0 and curuser ==request.user:
                    TodoList.objects.filter(user=request.user,  project=obj).delete()
                    obj.to_next()
                    History.objects.create(project=obj, user=request.user, pro_type=1)
                    msg += "提交成功，进入下一工作流 "+WORK_FLOW_NODE[obj.workflow_node][1]
                    if curuser == obj.starter:
                        Ds = Device.objects.filter(project_info = obj)
                        total = 0
                        for d in Ds:
                            total += d.get_total_sale_price()
                        print(total)
                        obj.total_price = total
                        obj.save()
                    if curuser == obj.manager:
                        ms = Material_use.objects.filter(project_info = obj)
                        hs = work_hour.objects.filter(project_info=obj)
                        total = 0
                        money = 0
                        for h in hs:
                            total += h.inside_work_hour + h.extra_work_hour
                            money += h.inside_work_hour *100 + h.extra_work_hour*200
                        obj.total_hour = total
                        total = 0
                        for m in ms:
                            total += m.total()
                        obj.total_mat = total
                        obj.total_money = total + money


                else:
                    '''History.objects.create(project=obj, user=request.user, pro_type=4)'''
                    msg += "不在您的工作流之中 "
                self.message_user(request, msg)


        else:

            obj.save()
            Outsource.objects.create(project_info=obj)
            Finish_report.objects.create(project_info=obj)
            History.objects.create(project=obj, user=request.user, pro_type=0)
            TodoList.objects.create(project=obj, user=request.user)

            feedback_report.objects.create(project_info = obj,idnum=1,item = '要货及施工计划',points = 6, standard='（1）施工前进行施工现场踏勘，提前消化合同执行报告，制定合理清晰的施工方案； ')
            feedback_report.objects.create(project_info = obj,idnum=1,item = '要货及施工计划',points = 2,standard='（2）内外部沟通协调顺畅； ')
            feedback_report.objects.create(project_info = obj,idnum=1,item = '要货及施工计划',points = 2,standard='（3）人员、设备、辅材辅料、配件、施工机具等准备充分合理； ')
            feedback_report.objects.create(project_info = obj,idnum=1,item = '要货及施工计划',points = 5,standard='（4）制定项目要货计划合理，货到公司库房不超过两周。')
            feedback_report.objects.create(project_info = obj,idnum=2,item = '进度',points = 15,standard=' 按施工进度计划施工作业，无特殊情况下能按时间节点管控工程，如期交付。')
            feedback_report.objects.create(project_info = obj,idnum=3,item = '质量',points = 3,standard='（1）产品保护良好；   ')
            feedback_report.objects.create(project_info = obj,idnum=3,item = '质量',points = 2,standard='（2）施工现场秩序井然，无脏、乱、差现象； ')
            feedback_report.objects.create(project_info = obj,idnum=3,item = '质量',points = 15,standard='（3）无较大质量问题，一次性通过外部验收，无整改或只有局部整改项。 ')
            feedback_report.objects.create(project_info=obj, idnum=4,item = '用料',points = 15,standard='根据最终出库数量和现场测量进行评定，若损耗＞10%，则此项计0分。')
            feedback_report.objects.create(project_info=obj, idnum=5,item = '用工',points = 5,standard='（1）工时绩效表中针对项目成员的工时考评合理；')
            feedback_report.objects.create(project_info=obj, idnum=5,item = '用工',points = 10,standard='（2）根据项目具体情况，总工时控制合理。')
            feedback_report.objects.create(project_info=obj, idnum=6,item = '安全规范',points = 5,standard=' 施工现场无违反安全作业规范行为。 ')
            feedback_report.objects.create(project_info=obj, idnum=7,item = '验收',points = 3,standard='（1） 验收电子及纸质资料：验收报告、施工日志、材料报验申请、设备移交记录、调试检测记录、试运行记录； ')
            feedback_report.objects.create(project_info=obj, idnum=7,item = '验收',points = 3,standard='（2）设备信息登录齐全； ')
            feedback_report.objects.create(project_info=obj, idnum=7,item = '验收',points = 4,standard='（3）对整改项及时处理无遗留问题； ')
            feedback_report.objects.create(project_info=obj, idnum=7,item = '验收',points = 2,standard='（4）积极及时协调客户、通知营销人员协调组织验收； ')
            feedback_report.objects.create(project_info=obj, idnum=8,item = '合理化建议',points = 3,standard=' 项目施工过程中提出合理化建议，完工后自觉进行总结并提交书面报告。')
            feedback_report.objects.create(project_info=obj, idnum=9, item='总分',points = 100,standard='')



    def delete_model(self, request, obj):
        curuser = None
        if request.user == obj.starter and FLOW_ROLES[obj.workflow_node][1] == '合同签约人':
            obj.active = False
            obj.name = obj.name + " 由合同签约人终止"
            TodoList.objects.filter(user=request.user, project=obj).delete()
            History.objects.create(project=obj, user=request.user, pro_type=3)
            return

        elif FLOW_ROLES[obj.workflow_node][1] == '项目经理':
            curuser = obj.manager
        else:
            curuser = user_models.Employee.objects.get(title=ROLES.index(FLOW_ROLES[obj.workflow_node][1]))

        if curuser == request.user:
            TodoList.objects.filter(user=request.user, project=obj).delete()
            obj.back()
            History.objects.create(project=obj, user=request.user, pro_type=2)
            self.message_user(request, "已反对，回到上一工作流 " + WORK_FLOW_NODE[obj.workflow_node][1])
        else:

            self.message_user(request, "不属于您的工作流， 当前流为" + WORK_FLOW_NODE[obj.workflow_node][1])
    def response_change(self, request, obj):
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.id) + '/change')

    def response_add(self, request, obj):
        return HttpResponseRedirect('/admin/basedata/todolist')





admin.site.register(Project,ProjectAdmin)


class OutsourceAdmin(admin.ModelAdmin):
    list_display = ['myname', 'begin_time', 'fuzeren', 'end_time', 'total_price']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(OutsourceAdmin, self).get_queryset(request)

        qs = super(OutsourceAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):


        show_submit_button = True

        extra_context = extra_context or {}

        ctx = dict(
            show_submit_button=show_submit_button,
            is_outSource=True,
            outSource_id = 2,
        )

        extra_context.update(ctx)
        return super(OutsourceAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        pro = form.cleaned_data.get('project_info')
        if request.user == pro.manager:
            self.message_user(request, "工作流内的修改")
            obj.save()
        else:
            str = "您无权对该项目  " + pro.name + " 的其他费用文件修改，修改失败"
            self.message_user(request, str)

    def delete_model(self, request, obj):
        pro = obj.project_info
        if request.user == pro.manager:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的其他费用文件修改，修改失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        return HttpResponseRedirect('/admin/')

    def response_add(self, request, obj):
        return HttpResponseRedirect('/admin/')


admin.site.register(Outsource,OutsourceAdmin)



class Outsource_itemsAdmin(admin.ModelAdmin):

    list_display = ['id','item_name','provider','num','price']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(Outsource_itemsAdmin, self).get_queryset(request)
        qs = super(Outsource_itemsAdmin, self).get_queryset(request)
        os = Outsource.objects.get(project_info= pro)
        return qs.filter(outsource_info=os)

    def changelist_view(self, request, extra_context=None):
        if tmp.proID != 0:
            if request.user == Project.objects.get(id=tmp.proID).manager:
                self.list_editable = ['item_name','provider','num','price']

            if len(Outsource_items.objects.filter(item_name = '---',outsource_info=Outsource.objects.get(project_info = Project.objects.get(id=tmp.proID))))>0:
                pass
            else:
                newobj = Outsource_items.objects.create(item_name = "---", provider = "---",outsource_info=Outsource.objects.get(project_info = Project.objects.get(id=tmp.proID)))
                newobj.save()
        else:
            self.message_user(request,"项目ID不存在，请重新获取")

        return super(Outsource_itemsAdmin, self).changelist_view(request, extra_context)


admin.site.register(Outsource_items,Outsource_itemsAdmin)


class DeviceRecord(admin.ModelAdmin):
    ordering = ['id']

    actions = ['get_total','get_total_inqury','get_total_buy']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(DeviceRecord, self).get_queryset(request)
        qs = super(DeviceRecord, self).get_queryset(request)
        return qs.filter(project_info=pro)

    def changelist_view(self, request, extra_context=None):
        print(request.user.title)
        if tmp.proID!=0:
            if request.user == Project.objects.get(id=tmp.proID).starter:
                self.list_display = ['id', 'name', 'brand', 'type', 'specification', 'num', 'unit', 'insurance',
                                         'sale_price', 'get_total_sale_price']
                self.list_editable = ['name', 'brand', 'type', 'specification', 'num', 'unit', 'insurance',
                                          'sale_price']
            elif request.user.title == 2:
                self.list_display = ['id','name', 'brand', 'type', 'specification', 'num', 'unit', 'insurance','sale_price',
                        'Inquiry_price','buy_from','buy_price']
                self.list_editable = ['Inquiry_price','buy_from','buy_price']

            elif request.user.title == 1 or  request.user.title == 3:
                self.list_display = ['id','name', 'brand', 'type', 'specification', 'num', 'unit', 'insurance','sale_price',
                        'Inquiry_price','buy_from','buy_price']
                self.list_editable = []
            else:
                self.list_display = ['id', 'name', 'brand', 'type', 'specification', 'num', 'unit', 'insurance', 'sale_price','get_total_sale_price']
                self.list_editable = []

        if tmp.proID != 0:
            if len(Device.objects.filter(name = '---',project_info=Project.objects.get(id = tmp.proID)))>0:
                pass
            else:
                newobj = Device.objects.create(name = "---", brand = "---",project_info=Project.objects.get(id = tmp.proID))
                newobj.save()
        else:
            self.message_user(request,"项目ID不存在，请重新获取")

        return super(DeviceRecord, self).changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """

        :param request:
        :param object_id:
        :param form_url:
        :param extra_context:
        :return:
        """
        show_submit_button = True
        show_save = True
        extra_context = extra_context or {}
        if request.user.title == 1 or request.user.title == 2 or request.user.title == 3:
            if request.user == user_models.Employee.objects.get(title = 2):
                show_save = True
        else:
            self.exclude = ('buy_price','Inquiry_price','buy_from')
        ctx = dict(

            show_submit_button=show_submit_button,
            show_save_and_add_another = True,
            show_delete_link = False,
            show_save_and_continue = False,
            show_save = show_save
        )

        extra_context.update(ctx)
        return super(DeviceRecord, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        pro = form.cleaned_data.get('project_info')
        if pro == None:
            pro = Project.objects.get(id = tmp.proID)
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        swb = user_models.Employee.objects.get(title = 2)
        if intodo.count()>0 and (request.user == pro.starter or request.user==swb):
            self.message_user(request, "成功")
            obj.save()
        elif inHis.count()>0 and (request.user == pro.starter or request.user==swb):
            self.message_user(request, "不再工作流内的修改")
            obj.save()
        else:
            str = "您无权对该项目  "+pro.name+" 的设备文件修改，修改失败"
            self.message_user(request, str)

    def delete_model(self, request, obj):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.starter:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的设备文件修改，修改失败"
            self.message_user(request, str)


    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def response_add(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def get_total(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if tmp.proID!=0:
            ds = Device.objects.filter(id__in=selected)
            total = 0
            for d in ds:
                total += d.get_total_sale_price()
            Device.objects.filter(name = '---').update(insurance='已选中总价',sale_price=total)

    get_total.short_description = "获取已选中总计单价"


    def get_total_inqury(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if tmp.proID!=0:
            ds = Device.objects.filter(id__in=selected)
            total = 0
            for d in ds:
                total += d.get_total_inquiry_price()
            Device.objects.filter(name = '---').update(insurance='已选中总价',Inquiry_price=total)

    get_total_inqury.short_description = "获取已选中总计询价单价"


    def get_total_buy(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if tmp.proID!=0:
            ds = Device.objects.filter(id__in=selected)
            total = 0
            for d in ds:
                total += d.get_total_buy_price()
            Device.objects.filter(name = '---').update(insurance='已选中总价',buy_price=total)

    get_total_buy.short_description = "获取已选中采购单价"

admin.site.register(Device,DeviceRecord)






class DeviceChange(admin.ModelAdmin):
    list_display = ['id','name', 'brand', 'type', 'specification', 'num', 'unit','sale_price','note']
    ordering = ['id']

    def get_readonly_fields(self, request, obj=None):
        return ['agreed','workflow_node']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(DeviceChange, self).get_queryset(request)
        qs = super(DeviceChange, self).get_queryset(request)
        return qs.filter(project_info=pro)


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        show_submit_button = True
        extra_context = extra_context or {}

        ctx = dict(
            show_submit_button=show_submit_button,

            show_save_and_continue=False
        )

        extra_context.update(ctx)
        return super(DeviceChange, self).changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if tmp.proID != 0:
            if request.user == Project.objects.get(id=tmp.proID).manager:
                self.list_editable = ['name', 'brand', 'type', 'specification', 'num', 'unit', 'sale_price'
                                        ,'note']
            elif request.user.title == 2:
                self.list_display = ['id','name', 'brand', 'type', 'specification', 'num', 'unit','sale_price','buy_price','note']
                self.list_editable = ['buy_price']
            elif request.user.title == 1 or request.user.title == 3:
                self.list_display = ['id', 'name', 'brand', 'type', 'specification', 'num', 'unit', 'sale_price',
                                     'buy_price', 'note']
                self.list_editable = []
            if len(Device_change.objects.filter(name='----', project_info=Project.objects.get(id=tmp.proID))) > 0:
                pass
            else:
                newobj = Device_change.objects.create(name="----", brand="---",
                                                      project_info=Project.objects.get(id=tmp.proID))
                newobj.save()
        else:
            self.message_user(request, "项目ID不存在，请重新获取")
            return super(DeviceChange, self).changelist_view(request, extra_context)
        can_submit =False
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=tmp.proID)
        if request.user == pro.manager:
            can_submit = True
        else:
            whs = mymodels.Device_change.objects.filter(project_info=pro)
            wh = whs[0]
            if wh.MYROLES[wh.workflow_node][1] == '完成':
                over = True
            else:
                print(wh.MYROLES[wh.workflow_node][1])
                next = user_models.Employee.objects.get(title=ROLES.index(wh.MYROLES[wh.workflow_node][1]))
                if request.user == next:
                    can_submit = True
        extra_context = extra_context or {}
        id = tmp.proID
        ctx = dict(
            can_submit=can_submit,
            type=1,
            instance_id=id
        )

        extra_context.update(ctx)
        return super(DeviceChange, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        pro = Project.objects.get(id = tmp.proID)
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if intodo.count()>0 and (request.user == pro.manager or request.user.title == 2):
            self.message_user(request, "工作流内的修改")
            ds = Device.objects.filter(name=obj.name, brand=obj.brand, type=obj.type, project_info=obj.project_info)
            if len(ds) == 0:
                self.message_user(request, obj.name + '在原项目清单不存在，添加')
                if obj.num < 1:
                    self.message_user(request, '数量为负数，无法添加')
            else:
                self.message_user(request, '已在原项目中找到')
            obj.save()
            if "_addanother" in request.POST:
                return HttpResponseRedirect('/admin/next/'+str(pro.id)+'/1/')
        elif inHis.count()>0 and (request.user == pro.manager or request.user.title == 2):
            self.message_user(request, "不在工作流内的修改")
            ds = Device.objects.filter(name=obj.name, brand=obj.brand, type=obj.type, project_info=obj.project_info)
            if len(ds) == 0:
                self.message_user(request, obj.name + '在原项目清单不存在，添加')
                if obj.num < 1:
                    self.message_user(request, '数量为负数，无法添加')
            else:
                self.message_user(request, '已在原项目中找到')
            obj.save()
        else:
            str = "您无权对该项目  "+pro.name+" 的设备更改文件修改，修改失败"
            self.message_user(request, str)


    def delete_model(self, request, obj):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.starter:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的设备更改文件修改，修改失败"
            self.message_user(request, str)


    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device_change/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def response_add(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device_change/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

admin.site.register(Device_change,DeviceChange)




class Material_useAdmin(admin.ModelAdmin):
    list_display = ['id','material_name', 'brand', 'guige', 'xinhao', 'num', 'unit', 'price','total']
    ordering = ['id']
    def get_readonly_fields(self, request, obj=None):
        return ['agreed','workflow_node']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            print("未找到")
            return super(Material_useAdmin, self).get_queryset(request)
        qs = super(Material_useAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)

    def changelist_view(self, request, extra_context=None):
        if len(Material_use.objects.filter(material_name='---', project_info=Project.objects.get(id=tmp.proID))) > 0:
            pass
        else:
            newobj = Material_use.objects.create(material_name="---", project_info=Project.objects.get(id=tmp.proID))
            newobj.save()

        over = False
        can_submit = False
        extra_context = extra_context or {}
        id = tmp.proID
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=tmp.proID)
        if request.user == pro.manager:
            can_submit = True
            self.list_editable= ['material_name', 'brand', 'guige', 'xinhao', 'num', 'unit']
        elif request.user.title == 6:
            self.list_editable = ['price']
            can_submit = True

        else:
            whs = mymodels.Material_use.objects.filter(project_info=pro)
            wh = whs[0]
            if wh.MYROLES[wh.workflow_node][1] == '完成':
                over = True
            else:
                if wh.MYROLES[wh.workflow_node][1] != '等待':
                    next = user_models.Employee.objects.get(title=ROLES.index(wh.MYROLES[wh.workflow_node][1]))
                    if request.user == next:
                        can_submit = True
        ctx = dict(
            can_submit=can_submit,
            type = 2,
            instance_id = id
        )

        extra_context.update(ctx)
        return super(Material_useAdmin, self).changelist_view(request, extra_context)


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        show_submit_button = True
        extra_context = extra_context or {}



        ctx = dict(
            show_submit_button=show_submit_button,

            show_save_and_continue=False,
        )

        extra_context.update(ctx)
        return super(Material_useAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.manager or request.user.title == 6:
            self.message_user(request, "成功")
            obj.save()
        else:
            str = "您无权对该项目  " + pro.name + " 的出库文件修改，删除失败"
            self.message_user(request, str)

    def delete_model(self, request, obj):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.starter:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的出库更改文件修改，修改失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/material_use/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def response_add(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/material_use/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')




admin.site.register(Material_use,Material_useAdmin)


class Device_finalAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'brand', 'type', 'specification', 'producer','produce_num','produce_time','place_keep','bill_num', 'price']
    def get_readonly_fields(self, request, obj=None):
        return ['agreed','workflow_node']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(Device_finalAdmin, self).get_queryset(request)
        qs = super(Device_finalAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)

    def changelist_view(self, request, extra_context=None):
        if len(Device_final.objects.filter(name='---', project_info=Project.objects.get(id=tmp.proID))) > 0:
            pass
        else:
            newobj = Device_final.objects.create(name="---", project_info=Project.objects.get(id=tmp.proID))
            newobj.save()
        can_submit = False
        extra_context = extra_context or {}
        id = tmp.proID
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=tmp.proID)
        if request.user == pro.manager:
            self.list_editable = ['name', 'brand', 'type', 'specification', 'producer','produce_num','produce_time','place_keep','bill_num', 'price']
            can_submit = True
        else:
            whs = mymodels.Device_final.objects.filter(project_info=pro)
            wh = whs[0]
            if wh.MYROLES[wh.workflow_node][1] == '完成':
                over = True
            else:
                if wh.MYROLES[wh.workflow_node][1]!='等待':
                    next = user_models.Employee.objects.get(title=ROLES.index(wh.MYROLES[wh.workflow_node][1]))
                    if request.user == next:
                        can_submit = True
        ctx = dict(
            can_submit=can_submit,
            type=3,
            instance_id=id
        )

        extra_context.update(ctx)
        return super(Device_finalAdmin, self).changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        show_submit_button = True
        extra_context = extra_context or {}

        ctx = dict(
            show_submit_button=show_submit_button,
            show_save_and_continue = False,
        )

        extra_context.update(ctx)
        return super(Device_finalAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.manager:
            self.message_user(request, "成功")
            obj.save()
        else:
            str = "您无权对该项目  " + pro.name + " 的最终设备文件修改，删除失败"
            self.message_user(request, str)

    def delete_model(self, request, obj):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.starter:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的最终设备文件修改，删除失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device_change/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def response_add(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/device_change/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')


admin.site.register(Device_final,Device_finalAdmin)

class work_hourAdmin(admin.ModelAdmin):
    list_display = ['id','employee', 'work_content','start_time','finish_time', 'inside_work_hour', 'extra_work_hour',]
    list_filter = ['employee', 'start_time']
    ordering = ['id']
    def get_readonly_fields(self, request, obj=None):
        return ['agreed','workflow_node']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(work_hourAdmin, self).get_queryset(request)
        qs = super(work_hourAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)

    def changelist_view(self, request, extra_context=None):
        if len(work_hour.objects.filter(work_content='---', project_info=Project.objects.get(id=tmp.proID))) > 0:
            pass
        else:
            newobj = work_hour.objects.create(work_content="---", project_info=Project.objects.get(id=tmp.proID))
            newobj.save()
        can_submit = False
        extra_context = extra_context or {}

        id = tmp.proID
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=id)
        if request.user == pro.manager:
            can_submit = True
            self.list_editable = ['employee', 'work_content','start_time','finish_time', 'inside_work_hour', 'extra_work_hour']

        else:
            whs = mymodels.work_hour.objects.filter(project_info=pro)
            wh = whs[0]
            if wh.MYROLES[wh.workflow_node][1] == '完成':
                over = True
            else:
                if wh.MYROLES[wh.workflow_node][1] == '等待':
                    self.message_user(request,"项目经理未添加文件,无法访问")
                    return super(work_hourAdmin, self).changelist_view(request, extra_context)
                next = user_models.Employee.objects.get(title=ROLES.index(wh.MYROLES[wh.workflow_node][1]))
                if request.user == next:
                    can_submit = True
        ctx = dict(
            can_submit=can_submit,
            type=5,
            instance_id=id
        )

        extra_context.update(ctx)
        return super(work_hourAdmin, self).changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        show_submit_button = True
        extra_context = extra_context or {}

        ctx = dict(
            show_submit_button=show_submit_button,

            show_save_and_add_another=False,
        )

        extra_context.update(ctx)
        return super(work_hourAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        pro = Project.objects.get(id= tmp.proID)
        if request.user == pro.manager:
            whs = work_hour.objects.filter(project_info=pro)
            if len(whs) >0:
                self.message_user(request, "工作流还原")
                TodoList.objects.filter(project = pro, content_type = 5).delete()
                for wh in whs:
                    wh.workflow_node = 0
                    wh.save()
            self.message_user(request, "修改成功")
            obj.save()
        else:
            str = "您无权对该项目  " + pro.name + " 的工时更改文件修改，修改失败"
            self.message_user(request, str)

    def delete_model(self, request, obj):
        pro = obj.project_info
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if request.user == pro.starter:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的工时文件修改，删除失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/work_hour/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')

    def response_add(self, request, obj):
        if "_addanother" in request.POST:
            return HttpResponseRedirect('/admin/basedata/work_hour/add/')
        return HttpResponseRedirect('/admin/basedata/project/' + str(obj.project_info.id) + '/change')


admin.site.register(work_hour,work_hourAdmin)

class Finish_reportAdmin(admin.ModelAdmin):
    list_display = ['project_info', 'time']
    ordering = ['id']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(Finish_reportAdmin, self).get_queryset(request)
        qs = super(Finish_reportAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)

    def get_readonly_fields(self, request, obj=None):
        return ['agreed','workflow_node']


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        show_save_and_continue = False
        show_submit_button = True
        show_save = False
        show_delete_link = False
        extra_context = extra_context or {}
        obj = Finish_report.objects.get(id=object_id)
        if request.user == obj.project_info.manager:
            show_save = True
        if obj.MYROLES[obj.workflow_node][1] == '完成':
            show_save_and_continue = False
        else:
            if obj.MYROLES[obj.workflow_node][1] == '等待':
                if request.user == obj.project_info.manager:
                    show_save = True
                    show_delete_link = True
                    show_save_and_continue = True
            else:
                curuser = user_models.Employee.objects.get(title=ROLES.index(obj.MYROLES[obj.workflow_node][1]))
                if curuser == request.user:
                    show_save_and_continue = True
        ctx = dict(
            show_submit_button=show_submit_button,
            show_save_and_continue=show_save_and_continue,
            show_save_and_add_another=False,
            show_delete_link=show_delete_link,
            show_save=show_save

        )

        extra_context.update(ctx)
        return super(Finish_reportAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):

        if "_next" in request.POST:
            return
        pro = form.cleaned_data.get('project_info')
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if intodo.count() > 0 and request.user == pro.manager:
            self.message_user(request, "工作流内的修改")
            obj.save()
            return
        elif inHis.count() > 0 and request.user == pro.manager:
            self.message_user(request, "不在工作流内的修改")
            obj.save()
        else:
            strr = "您无权对该项目  " + pro.name + " 的竣工报告文件修改"
            self.message_user(request, strr)

    def delete_model(self, request, obj):
        pro = obj.project_info
        if request.user == pro.manager:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的竣工报告文件修改，修改失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        if "_next" in request.POST:
            pro = obj.project_info
            if obj.MYROLES[obj.workflow_node][1]== '等待':
                if pro.manager == request.user:
                    c = str(pro.id)
                    self.message_user(request, '项目已同意，进入下一流程 ' + str(obj.MYROLES[obj.workflow_node+1][1]))
                    return HttpResponseRedirect('/next/' + '6/' + c)
            else:
                curuser = user_models.Employee.objects.get(title=ROLES.index(obj.MYROLES[obj.workflow_node][1]))
                if curuser == request.user:
                    self.message_user(request, '项目已同意，进入下一流程 ' + str(obj.MYROLES[obj.workflow_node+1][1]))
                    c = str(pro.id)
                    return HttpResponseRedirect('/next/' + '4/' + c)

        return HttpResponseRedirect('/admin/basedata/project/'+str(obj.project_info.id)+'/change')

    def response_add(self, request, obj):
        return HttpResponseRedirect('/admin/')


admin.site.register(Finish_report,Finish_reportAdmin)





class feedback_reportAdmin(admin.ModelAdmin):
    list_display = ['idnum', 'item', 'standard', 'points', 'self_eva', 'eva', 'note', 'bonus']
    ordering = ['idnum']
    actions = ['get_total_eva']

    def get_queryset(self, request):
        pros = ContentType.objects.get(app_label='basedata', model='project')
        try:
            pro = pros.model_class().objects.get(id=tmp.proID)
        except Exception as e:
            return super(feedback_reportAdmin, self).get_queryset(request)
        qs = super(feedback_reportAdmin, self).get_queryset(request)
        return qs.filter(project_info=pro)
    def get_readonly_fields(self, request, obj=None):
        return ['agreed', 'workflow_node']
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        show_save_and_continue = False
        show_submit_button = True
        show_save = False
        show_delete_link = False
        extra_context = extra_context or {}
        obj = feedback_report.objects.get(id=object_id)
        if request.user == obj.project_info.manager:
            show_save = True
        if obj.MYROLES[obj.workflow_node][1] == '完成':
            show_save_and_continue = False
        else:
            if obj.MYROLES[obj.workflow_node][1] == '等待':
                if request.user == obj.project_info.manager:
                    show_save = True
                    show_delete_link = True
                    show_save_and_continue = True
            else:
                curuser = user_models.Employee.objects.get(title=ROLES.index(obj.MYROLES[obj.workflow_node][1]))
                if curuser == request.user:
                    show_save_and_continue = True
        ctx = dict(
            show_submit_button=show_submit_button,
            show_save_and_continue = show_save_and_continue,
            show_save_and_add_another=False,
            show_delete_link=show_delete_link,
            show_save=show_save

        )

        extra_context.update(ctx)
        return super(feedback_reportAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if tmp.proID != 0:
            if request.user == Project.objects.get(id=tmp.proID).manager:
                self.list_editable = ['self_eva','note']
            elif request.user.title == 4 or request.user.title == 5:
                self.list_editable = ['eva','note']
        else:
            self.message_user(request, "项目ID不存在，请重新获取")
            return super(feedback_reportAdmin, self).changelist_view(request, extra_context)
        can_submit = False
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=tmp.proID)
        if request.user == pro.manager:
            can_submit = True
        else:
            whs = mymodels.feedback_report.objects.filter(project_info=pro)
            wh = whs[0]
            if wh.MYROLES[wh.workflow_node][1] == '完成':
                over = True
            else:
                if wh.MYROLES[wh.workflow_node][1] != '等待':
                    next = user_models.Employee.objects.get(title=ROLES.index(wh.MYROLES[wh.workflow_node][1]))
                    if request.user == next:
                        can_submit = True
        extra_context = extra_context or {}
        id = tmp.proID
        ctx = dict(
            can_submit=can_submit,
            type=6,
            instance_id=id
        )

        extra_context.update(ctx)
        return super(feedback_reportAdmin, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):

        if "_next" in request.POST:
            return
        pro = Project.objects.get(id =tmp.proID)
        intodo = TodoList.objects.filter(user=request.user, project=pro)
        inHis = History.objects.filter(user=request.user, project=pro)
        if intodo.count() > 0 and (request.user == pro.manager or request.user.title == 5 or request.user.title==4):
            self.message_user(request, "工作流内的修改")
            obj.save()
            return
        elif inHis.count() > 0 and (request.user == pro.manager or request.user.title == 5 or request.user.title==4):
            self.message_user(request, "不在工作流内的修改")
            obj.save()
        else:
            str = "您无权对该项目  " + pro.name + " 的竣工报告文件修改，修改失败"
            self.message_user(request, str)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        ctx = dict(
            show_save_and_add_another=False,

        )
        extra_context['show_save_and_add_another'] = False

        extra_context.update(ctx)
        return super(feedback_reportAdmin, self).change_view(request, object_id, form_url, extra_context)
    def delete_model(self, request, obj):
        pro = obj.project_info
        if request.user == pro.manager:
            self.message_user(request, "删除成功")
            obj.delete()
        else:
            str = "您无权对该项目  " + pro.name + " 的项目经理自评文件修改，修改失败"
            self.message_user(request, str)

    def response_change(self, request, obj):
        if "_next" in request.POST:
            pro = obj.project_info
            if obj.MYROLES[obj.workflow_node][1]== '等待':
                if pro.manager == request.user:
                    c = str(pro.id)
                    self.message_user(request, '项目已同意，进入下一流程 ' + str(obj.MYROLES[obj.workflow_node+1][1]))
                    return HttpResponseRedirect('/next/' + '6/' + c)
            else:
                curuser = user_models.Employee.objects.get(title=ROLES.index(obj.MYROLES[obj.workflow_node][1]))
                if curuser == request.user:
                    self.message_user(request, '项目已同意，进入下一流程 ' + str(obj.MYROLES[obj.workflow_node+1][1]))
                    c = str(pro.id)
                    return HttpResponseRedirect('/next/' + '6/' + c)

        return HttpResponseRedirect('/admin/basedata/project/'+str(obj.project_info.id)+'change')

    def response_add(self, request, obj):
        return HttpResponseRedirect('/admin/')



    def get_total_eva(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if tmp.proID != 0:
            ds = feedback_report.objects.filter(id__in=selected)
            total = 0
            total_self = 0
            for d in ds:
                total_self += d.self_eva
                total += d.eva
            feedback_report.objects.filter(idnum=9).update(self_eva=total_self,eva=total)

    get_total_eva.short_description = "获取已选中总分"


admin.site.register(feedback_report,feedback_reportAdmin)


class HistoryAdmin(admin.ModelAdmin):
    list_display = ['project', 'href', 'memo', 'pro_type', 'pro_time']
    filter = ['project','pro_type']
    def get_queryset(self, request):
        qs = super(HistoryAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user=request.user)


admin.site.register(History, HistoryAdmin)


class TodoListAdmin(admin.ModelAdmin):
    list_display = ['code', 'project','content_type', 'href', 'is_read', 'status', 'arrived_time']
    list_filter = ['status','user']

    def get_queryset(self, request):
        qs = super(TodoListAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user=request.user)



admin.site.register(TodoList, TodoListAdmin)




