from django.http.response import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from basedata import admin
from basedata import models

from users import models as user_models


ProjID = 0

def home(request):
    return HttpResponseRedirect("/admin")

def deviceInfo(request,project_id):
    admin.tmp.proID = project_id
    return HttpResponseRedirect("/admin/basedata/device")

def deviceChange(request,project_id):
    admin.tmp.proID = project_id
    return HttpResponseRedirect("/admin/basedata/device_change")

def deviceFinal(request,project_id):
    admin.tmp.proID = project_id
    return HttpResponseRedirect("/admin/basedata/device_final")

def stock(request,project_id):
    admin.tmp.proID = project_id
    return HttpResponseRedirect("/admin/basedata/material_use")

def workH(request,project_id):

    admin.tmp.proID = project_id
    return HttpResponseRedirect("/admin/basedata/work_hour")

def outItem(request,outSource_id):

    ProjID = outSource_id
    return HttpResponseRedirect("/admin/basedata/outsource_items")

def finalReport(request,project_id):
    pro = models.Project.objects.get(id = str(project_id))
    frs = ContentType.objects.get(app_label='basedata', model='Finish_report')
    fr = frs.model_class().objects.get(project_info=pro)
    return HttpResponseRedirect('/admin/basedata/finish_report/'+str(fr.id)+'/change')


def Evalu(request,project_id):
    return HttpResponseRedirect('/admin/basedata/feedback_report')

def outSource(request,project_id):
    pros = ContentType.objects.get(app_label='basedata', model='project')
    pro = pros.model_class().objects.get(id=project_id)
    frs = ContentType.objects.get(app_label='basedata', model='outsource')
    fr = frs.model_class().objects.get(project_info=pro)
    return HttpResponseRedirect('/admin/basedata/outsource/'+str(fr.id)+'/change')

def next(request,type,project_id):
    RANK = {'普通员工': 0, '总经理': 1, '商务经理': 2, '财务经理': 3, '工程经理': 4, '技术经理': 5, '库管': 6, '营销经理': 7, '行政经理':8}
    dict ={ 1:'Device_change',2: 'Material_use', 3:'Device_final', 4:'Finish_report', 5:'work_hour', 6:'feedback_report'}
    try:
        pros = ContentType.objects.get(app_label='basedata', model='project')
        pro = pros.model_class().objects.get(id=project_id)
        subjects = ContentType.objects.get(app_label='basedata', model=dict[type])
        subject = subjects.model_class().objects.filter(project_info = pro)
        for sub in subject:
            sub.to_next()
        if len(subject)>0:

            if subject[0].MYROLES[subject[0].workflow_node][1]=='完成':
                if type == 1:
                    for sub in subject:
                        dss = ContentType.objects.get(app_label='basedata', model='device')
                        ds = dss.model_class().objects.filter(name=sub.name, brand=sub.brand, type=sub.type,
                                                              project_info=sub.project_info)
                        if len(ds) == 0:
                            print('adding')
                            if sub.name != '----':
                                dss.model_class().objects.create(name=sub.name, brand=sub.brand, type=sub.type,
                                                             project_info=sub.project_info,
                                                             specification=sub.specification, num=sub.num,
                                                             unit=sub.unit, sale_price=sub.sale_price)
                        else:
                            print('changing')
                            d = ds[0]
                            ornum = d.num
                            d.num +=ornum
                            dss.model_class().objects.filter(num=0).delete()

                        total = 0
                        #change the total price in the project due to the change of the devices
                        for di in ds:
                            total += di.sale_price
                        pro.total_price = total
                        d.save()
                memo = "提交了 " + subject[0]._meta.verbose_name.title() + " 分项目完成"
                models.History.objects.create(project=pro, user=request.user, pro_type=5, memo=memo)
                models.TodoList.objects.get(project=pro, user=request.user, content_type=type).delete()

                return HttpResponseRedirect('/admin/basedata/history/')

            nextUser = user_models.Employee.objects.get(title=RANK[subject[0].MYROLES[subject[0].workflow_node][1]])
            models.TodoList.objects.create(project=pro, user=nextUser, content_type=type)
            memo = "提交了 " + subject[0]._meta.verbose_name.title() + "下一节点是 " + subject[0].MYROLES[subject[0].workflow_node][1]
            models.History.objects.create(project=pro, user=request.user, pro_type=5, memo=memo)
            if request.user != pro.manager:
                models.TodoList.objects.get(project=pro, user=request.user, content_type=type).delete()
        else:
            print("没有数据")

        return HttpResponseRedirect('/admin/basedata/history/')
    except Exception as e:
        print(e)



