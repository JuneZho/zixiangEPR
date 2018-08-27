# _*_ coding:utf-8 _*_
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from common import const
from common import generic
from users import models as user_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
# Create your models here.
DEP_CHOICE = (('shangwu',u"商务部"),('caiwu', u"财务部"),('yinxiao', u"营销部"),
    ('jisu', u"技术部"),
    ('others', u"其他"),
    ('xiagnmu', u"项目部"),
    ('gongchen', u"工程部"),
    ('xinzheng', u"行政部"))

ROLES = ((0, u"合同签约人"),
    (1, u"商务经理"),
    (2, u"财务经理"),
    (3, u"营销经理"),
    (4, u"总经理"),
    (5, u"工程经理"),
    (6, u"项目经理"),
    (7, u"工程经理"),
    (8, u"技术经理"),
    (9, u"总经理"))

PROCESS_TYPE = (
    (0, u"提交"),
    (1, u"同意"),
    (2, u"反对"),
    (3, u"终止"))

BRAND_CHOICE = (("Epson",u"爱普生"),("Lenovo",u"联想"))

UNIT_CHOICE = ((u"个",u"个"),(u"只",u"只"))







class Project(models.Model):
    """
    工程项目
    """
    budge = 0
    index_weight = 1

    active = models.BooleanField(verbose_name=u'状态',default=True)
    begin = models.DateField(_('开始日期'), blank=True, null=True)

    starter = models.ForeignKey(user_models.Employee,verbose_name=u"合同签约人",on_delete=models.CASCADE)
    name = models.CharField(verbose_name=u"执行编号", max_length=const.DB_CHAR_NAME_20)
    cusname = models.CharField(verbose_name=u"客户单位",max_length=const.DB_CHAR_NAME_20,default='无')
    cusaddr = models.CharField(verbose_name=u"客户地址",max_length=const.DB_CHAR_NAME_40,default='无')
    recname = models.CharField(verbose_name=u"收货单位",max_length=const.DB_CHAR_NAME_20,default='无')
    recaddr = models.CharField(verbose_name=u"收货地址",max_length=const.DB_CHAR_NAME_40,default='无')

    receiver = models.CharField(verbose_name=u"收货人", max_length=const.DB_CHAR_CODE_10,default='无')
    receiverdep = models.CharField(_(u"收货部门"),max_length=const.DB_CHAR_NAME_20,default='无')
    receiverphone = models.CharField(_(u"收货手机"),max_length=const.DB_CHAR_NAME_20,default='无')
    receivertele = models.CharField(_(u"收货电话"), max_length=const.DB_CHAR_NAME_20,default='无')
    payer = models.CharField(verbose_name=u"付款人", max_length=const.DB_CHAR_CODE_10,default='无')
    payerdep = models.CharField(_(u"付款部门"), max_length=const.DB_CHAR_NAME_20,default='无')
    payerphone = models.CharField(_(u"付款手机"), max_length=const.DB_CHAR_NAME_20,default='无')
    payertele = models.CharField(_(u"付款手机"), max_length=const.DB_CHAR_NAME_20,default='无')

    total_price = models.DecimalField(verbose_name=u"合同金额",max_length=const.DB_CHAR_CODE_10,default=0,blank=True, null=True,max_digits=8,decimal_places=2)
    end = models.DateField(_('完工日期'), blank=True, null=True)
    kaipiao = models.BooleanField(_(u"开票"),default=False)
    niehe_hour = models.PositiveIntegerField(verbose_name=u'内核工时数',null= True, blank= True)
    total_hour = models.PositiveIntegerField(verbose_name=u'总工时',null= True, blank= True)
    total_mat = models.PositiveIntegerField(verbose_name=u'材料金额',null= True, blank= True)
    total_money = models.PositiveIntegerField(verbose_name=u'总金额',null= True, blank= True)


    description = models.TextField(verbose_name=u"其他",blank=True,null=True)

    manager = models.ForeignKey(user_models.Employee,verbose_name=u"项目经理",related_name=u"被指派项目经理",blank=True,null=True,on_delete=models.CASCADE)

    comment = models.CharField(_(u"批示"), max_length=const.DB_CHAR_NAME_120,default='无',blank=True,null=True)
    associated_file = models.FileField(_("文件"),upload_to='project',blank=True,null=True)

    """工作流"""
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

    RANK = {'普通员工': 0, '总经理': 1, '商务经理': 2,'财务经理': 3, '工程经理': 4, '技术经理': 5 ,'库管': 6, '营销经理': 7}




    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=WORK_FLOW_NODE)

    def get_curr_node(self):
        if self.workflow_node<20:
            return self.get_workflow_node_display()
        else:
            return "项目节点错误"

    def to_next(self):
        if self.workflow_node ==9:
            import datetime
            self.end = datetime.datetime.now()
            self.workflow_node += 1
        elif self.workflow_node <9:
            self.workflow_node+=1
            self.save()
            if ROLES[self.workflow_node][1] == '项目经理':
                user = self.manager
            else:
                user = user_models.Employee.objects.get(title=self.RANK[ROLES[self.workflow_node][1]])
            TodoList.objects.create(project=self, user=user , memo = "上一节点为 "+ROLES[self.workflow_node-1][1])
        else:
            print("已终结或暂挂，无法流程继续")

    def back(self):
        self.workflow_node -= 1
        self.save()
        user = user_models.Employee.objects.get(title=self.RANK[ROLES[self.workflow_node][1]])
        TodoList.objects.create(project=self, user=user, memo="项目由 "+ROLES[self.workflow_node+1][1]+" 退回")


    def __str__(self):
        return self.name

    def get_project(self):
        return

    def get_all_devices_price(self):
        ds = Device.objects.filter(project_info=self)
        total = 0
        for d in ds:
            total += d.get_total_sale_price()
        return total

    class Meta:
        verbose_name = u"项目"
        verbose_name_plural = u"项目"



class Device(models.Model):
    project_info = models.ForeignKey(Project, on_delete=models.CASCADE,verbose_name=u"所属项目", null=True)


    thisid = models.IntegerField(default=0,verbose_name="ID")
    name = models.CharField(max_length=20, default="", verbose_name=u"设备名称",blank=True, null=True)
    brand = models.CharField(verbose_name=u"品牌",max_length=const.DB_CHAR_NAME_20,choices=BRAND_CHOICE,blank=True, null=True)
    type = models.CharField(verbose_name=u"型号",max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    specification = models.CharField(verbose_name=u"规格",max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    num = models.IntegerField(verbose_name=u"数量",blank=True, null=True)
    unit = models.CharField(verbose_name=u"单位",max_length=const.DB_CHAR_CODE_4,choices=UNIT_CHOICE,blank=True, null=True)
    sale_price = models.DecimalField(verbose_name=u"单价",max_length=const.DB_CHAR_CODE_8,default=1,blank=True, null=True,max_digits=7,decimal_places=2)
    insurance = models.CharField(verbose_name=u"保修", max_length=const.DB_CHAR_CODE_10, default=u"无", blank=True,
                                 null=True)
    Inquiry_price = models.DecimalField(verbose_name=u"询价单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True, null=True, max_digits=7, decimal_places=2)
    insurance_g = models.CharField(verbose_name=u"保修承诺", max_length=const.DB_CHAR_CODE_10, default=u"无", blank=True,
                                 null=True)
    buy_from = models.CharField(verbose_name=u"供应商", max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    buy_price = models.DecimalField(verbose_name=u"采购单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                    null=True, max_digits=7, decimal_places=2)
    insurance_to = models.DateField(verbose_name=u"保修期至", blank=True, null=True)
    time_deliver = models.DateField(verbose_name=u"到货期", blank=True, null=True)

    MYROLES = ((0, u"等待"),
             (1, u"商务部"),
             (2, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=ROLES)
    def __str__(self):
        return self.project_info.name + "的设备"+str(self.thisid)



    def get_total_sale_price(self):
        title = u'金额'
        if self.num!=None and self.sale_price!=None:
            return self.sale_price* self.num
        else:
            return 0

    def get_total_inquiry_price(self):

        if self.num!=None and self.sale_price!=None:
            return self.Inquiry_price * self.num

    def get_total_buy_price(self):

        if self.num!=None and self.sale_price!=None:
            return self.buy_price * self.num

    get_total_sale_price.allow_tags = True
    get_total_sale_price.short_description = _("金额")

    class Meta:
        verbose_name=u"设备清单"
        verbose_name_plural=u"设备清单"


class Device_change(models.Model):

    thisid = models.IntegerField(default=0,verbose_name="ID")
    name = models.CharField(max_length=20, default="", verbose_name=u"设备名称", blank=True, null=True)
    brand = models.CharField(verbose_name=u"品牌", max_length=const.DB_CHAR_NAME_20, choices=BRAND_CHOICE, blank=True,
                             null=True)
    type = models.CharField(verbose_name=u"型号", max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    specification = models.CharField(verbose_name=u"规格", max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    num = models.IntegerField(verbose_name=u"数量", blank=True, null=True)
    unit = models.CharField(verbose_name=u"单位", max_length=const.DB_CHAR_CODE_4, choices=UNIT_CHOICE, blank=True,
                            null=True)
    sale_price = models.DecimalField(verbose_name=u"单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                     null=True, max_digits=7, decimal_places=2)
    buy_price = models.DecimalField(verbose_name=u"成本单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                    null=True, max_digits=7, decimal_places=2)
    note = models.CharField(max_length=const.DB_CHAR_NAME_40, default="", verbose_name=u"备注", blank=True, null=True)


    project_info = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=u"所属项目", null=True)
    agreed = models.BooleanField(verbose_name=u"已同意", default=False)
    MYROLES = ((0, u"等待"),
             (1, u"技术经理"),
             (2, u"商务经理"),
             (3, u"营销经理"),
             (4, u"总经理"),
             (5, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def get_total_sale_price(self):
        if self.num != None and self.sale_price != None:
            return self.sale_price * self.num
        else:
            return 0
    def get_total_buy_price(self):
        return self.buy_price * self.num
    def __str__(self):
        return self.project_info.name + "的设备更改"

    def to_next(self):
        if self.workflow_node < len(self.MYROLES) - 2:
            self.workflow_node += 1
        elif self.workflow_node == len(self.MYROLES) - 2:
            self.workflow_node += 1
            self.agreed = True

        self.save()

    def back_to(self, node_num):
        self.workflow_node = node_num

    def deny_table(self):
        self.workflow_node = 0

    class Meta:
        verbose_name = u"设备更改"
        verbose_name_plural = u"设备更改"


class Outsource(models.Model):

    project_info = models.OneToOneField(Project, on_delete=models.CASCADE, verbose_name=u"项目信息",blank=True, null=True)
    myname = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"营销员", blank=True, null=True)
    begin_time = models.DateField(verbose_name=u"计划开工时间",blank=True,null=True)
    end_time = models.DateField(verbose_name=u"计划竣工时间",blank=True,null=True)
    description = models.TextField(default="", verbose_name=u"工作内容", blank=True, null=True)
    fuzeren = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"项目负责人", blank=True, null=True)
    total_price = models.DecimalField(verbose_name=u"总价", max_length=const.DB_CHAR_CODE_10, default=0, blank=True,
                                     null=True, max_digits=10, decimal_places=2)

    agreed = models.BooleanField(verbose_name=u"已同意", default=False)
    MYROLES = ((0, u"等待"),
               (1, u"项目经理"),
               (2, u"工程经理"),
               (3, u"技术经理"),
               (4, u"总经理"),
               (5, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)
    class Meta:
        verbose_name = u"其他费用"
        verbose_name_plural = u"其他费用"

    def __str__(self):
        return self.project_info.name + "的其他费用表"


class Outsource_items(models.Model):

    thisid = models.IntegerField(default=0,verbose_name="ID")
    outsource_info = models.ForeignKey(Outsource,on_delete=models.CASCADE,verbose_name=u"所属外包项目",blank=True, null=True)
    item_name = models.CharField(max_length=const.DB_CHAR_NAME_20,default="",verbose_name=u"外包施工单位名称",blank=True, null=True)
    provider = models.CharField(max_length=const.DB_CHAR_NAME_20,default="",verbose_name=u"外包施工负责人",blank=True, null=True)
    num = models.IntegerField(default=1,validators=[MaxValueValidator(10),MinValueValidator(0)],verbose_name=u"外包数量")
    price = models.DecimalField(verbose_name=u"单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                     null=True, max_digits=7, decimal_places=2)
    note = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"备注", blank=True, null=True)

    def get_total(self):
        return self.num * self.price


    def __str__(self):
        return self.outsource_info.project_info.name + "的外包明细"
    class Meta:
        verbose_name = u"外包项目明细"
        verbose_name_plural = u"外包项目明细"


class Material_use(models.Model):
    project_info = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=u"所属项目", null=True)
    material_name = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"名称", blank=True, null=True)
    brand = models.CharField(verbose_name=u"品牌", max_length=const.DB_CHAR_NAME_20, choices=BRAND_CHOICE, blank=True,
                             null=True)
    guige = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"规格", blank=True,
                                     null=True)
    xinhao = models.CharField(max_length=const.DB_CHAR_CODE_10, default="", verbose_name=u"型号", blank=True,
                                     null=True)
    num = models.IntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(0)], verbose_name=u"数量")
    unit = models.CharField(verbose_name=u"单位", max_length=const.DB_CHAR_CODE_4, choices=UNIT_CHOICE, blank=True,
                            null=True)

    price = models.DecimalField(verbose_name=u"单价", max_length=const.DB_CHAR_CODE_8, blank=True,
                                     null=True, max_digits=7, decimal_places=2)

    agreed = models.BooleanField(verbose_name=u"已同意",default=False)

    MYROLES = ((0, u"等待"),
             (1, u"库管"),
             (2, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def __str__(self):
        return self.project_info.name + "的施工材料领用"

    def to_next(self):
        if self.workflow_node < len(self.MYROLES) - 2:
            self.workflow_node += 1
        elif self.workflow_node == len(self.MYROLES) - 2:
            self.workflow_node += 1
            self.agreed = True
        self.save()

    def total(self):
        title = u'金额'
        if self.num != None and self.price != None:
            return self.price * self.num
        else:
            return  0
    total.allow_tags = True
    total.short_description = _("金额")

    def back_to(self, node_num):
        if node_num<3:
            self.workflow_node = node_num
        else:
            print("num is too large")

    def deny_table(self):
        self.workflow_node = 0

    class Meta:
        verbose_name = u"材料领用"
        verbose_name_plural = u"材料领用"

class Device_final(models.Model):

    thisid = models.IntegerField(default=0,verbose_name="ID")
    name = models.CharField(max_length=20, default="", verbose_name=u"设备名字",blank=True, null=True)
    brand = models.CharField(verbose_name=u"品牌",max_length=const.DB_CHAR_NAME_20,choices=BRAND_CHOICE,blank=True, null=True)
    type = models.CharField(verbose_name=u"型号",max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    specification = models.CharField(verbose_name=u"规格",max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    producer = models.CharField(verbose_name=u"生产厂家",max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    produce_num = models.CharField(verbose_name=u"出产编号", max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    produce_time = models.DateField(verbose_name=u"出厂日期",blank = True, null = True)
    place_keep = models.CharField(verbose_name=u"存放地点", max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    bill_num = models.CharField(verbose_name=u"单据号", max_length=const.DB_CHAR_CODE_10, blank=True, null=True)
    price = models.DecimalField(verbose_name=u"单价", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                    null=True, max_digits=7, decimal_places=2)
    time_install = models.DateField(verbose_name=u"安装日期", blank=True, null=True)
    project_info = models.ForeignKey(Project, on_delete=models.CASCADE,verbose_name=u"所属项目", null=True)
    record = models.CharField(verbose_name=u"维修记录", max_length=const.DB_CHAR_NAME_120, blank=True, null=True)
    note = models.CharField(verbose_name=u"备注", max_length=const.DB_CHAR_NAME_120, blank=True, null=True)
    agreed = models.BooleanField(verbose_name=u"已同意", default=False)

    MYROLES = ((0, u"等待"),
             (1, u"工程经理"),
             (2, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def __str__(self):
        return self.project_info.name + "的设备信息表"
    def to_next(self):
        if self.workflow_node < len(self.MYROLES) - 2:
            self.workflow_node += 1


        elif self.workflow_node == len(self.MYROLES) - 2:
            self.workflow_node += 1
            self.agreed = True

        self.save()
    def back(self, node_num):
        if node_num < 3:
            self.workflow_node = node_num
        else:
            print("num is too large")

    def deny_table(self):
        self.workflow_node = 0

    class Meta:
        verbose_name=u"设备信息"
        verbose_name_plural=u"设备信息"


class Finish_report(models.Model):

    project_info = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=u"所属项目", null=True)
    time = models.DateField(verbose_name=u"日期", auto_now_add=True, blank=True, null=True)
    details = models.TextField(verbose_name=u"报告", blank=True, null=True)
    agreed = models.BooleanField(verbose_name=u"已同意", default=False)
    MYROLES = ((0, u"等待"),
             (1, u"工程经理"),
             (2, u"完成"))

    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def to_next(self):
        if self.workflow_node < len(self.MYROLES) - 2:
            self.workflow_node += 1
        elif self.workflow_node == len(self.MYROLES) - 2:
            self.workflow_node += 1
            self.agreed = True
        self.save()
    def back_to(self, node_num):
        if node_num < 3:
            self.workflow_node = node_num
        else:
            print("num is too large")

    def deny_table(self):
        self.workflow_node = 0

    def __str__(self):
        return self.project_info.name + "的竣工报告"

    class Meta:
        verbose_name=u"竣工报告"
        verbose_name_plural=u"竣工报告"


class work_hour(models.Model):

    thisid = models.IntegerField(default=0,verbose_name="ID")
    input_date = models.DateField(verbose_name=u"填写日期", auto_now_add=True, blank=True, null=True)
    employee = models.ForeignKey(user_models.Employee,verbose_name=u"员工",blank=True, null=True,on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name=u"开始日期", blank=True, null=True)
    finish_time = models.DateTimeField(verbose_name=u"结束日期", blank=True, null=True)
    work_content = models.CharField(verbose_name=u"工作内容", max_length=const.DB_CHAR_NAME_120, blank=True, null=True)
    inside_work_hour = models.IntegerField(default=0,verbose_name=u"上班工时/单价100")
    extra_work_hour = models.IntegerField(default=0, verbose_name=u"加班工时/单价200")
    project_info = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=u"所属项目", null=True)
    agreed = models.BooleanField(verbose_name=u"已同意", default=False)

    MYROLES = ((0, u"等待"),
             (1, u"工程经理"),
             (2, u"技术经理"),
             (3, u"行政经理"),
             (4, u"完成"))
    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def to_next(self):
        if self.workflow_node < len(self.MYROLES)-2:
            self.workflow_node += 1
        elif self.workflow_node == len(self.MYROLES)-2:
            self.workflow_node += 1
            self.agreed = True
        self.save()
    def back_to(self, node_num):
        if node_num < 3:
            self.workflow_node = node_num
        else:
            print("num is too large")

    def deny_table(self):
        self.workflow_node = 0

    class Meta:
        verbose_name = u"设备信息"
        verbose_name_plural = u"设备信息"

    class Meta:
        verbose_name = u"工时记录"
        verbose_name_plural = u"工时记录"


class feedback_report(models.Model):
    project_info = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=u"所属项目", null=True)
    idnum = models.PositiveIntegerField(verbose_name=u"序号", blank=True, null=True)
    item =  models.CharField(verbose_name=u"考核项目",max_length=const.DB_CHAR_NAME_40,blank=True, null=True)
    standard = models.CharField(verbose_name=u"考核标准",max_length=const.DB_CHAR_NAME_200,blank=True, null=True)
    points = models.PositiveIntegerField(verbose_name=u"分值")
    self_eva = models.PositiveIntegerField(verbose_name="自评分",default=0)
    eva = models.PositiveIntegerField(verbose_name="得分",default=0)
    note = models.CharField(verbose_name=u"备注",max_length=const.DB_CHAR_NAME_60,blank=True, null=True)
    bonus = models.DecimalField(verbose_name=u"项目经理奖励金额", max_length=const.DB_CHAR_CODE_8, default=1, blank=True,
                                    null=True, max_digits=7, decimal_places=2)
    agreed = models.BooleanField(verbose_name=u"已同意", default=False)

    MYROLES = ((0, u"等待"),
             (1, u"工程经理"),
             (2, u"技术经理"),
             (3, u"总经理"),
             (4, u"完成"))
    workflow_node = models.IntegerField(default=0, verbose_name=u"工作流节点", choices=MYROLES)

    def to_next(self):
        if self.workflow_node < len(self.MYROLES) - 2:
            self.workflow_node += 1
        elif self.workflow_node == len(self.MYROLES) - 2:
            self.workflow_node += 1
            self.agreed = True
        self.save()
    def back_to(self, node_num):
        if node_num < 3:
            self.workflow_node = node_num
        else:
            print("num is too large")


    def deny_table(self):
        self.workflow_node = 0

    class Meta:
        verbose_name = u"项目经理考核"
        verbose_name_plural = u"项目经理考核"


"""work flow model"""






class History(models.Model):
    """
    workflow history
    """
    PROCESS_TYPE = (
        (0, u"提交"),
        (1, u"同意"),
        (2, u"反对"),
        (3, u"终止"),
        (4, u"修改"),
        (5, u"分流程"),

    )
    index_weight = 5

    project = models.ForeignKey(Project,verbose_name=_("项目"),on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(user_models.Employee, verbose_name=u"用户", on_delete=models.CASCADE)
    pro_time = models.DateTimeField(verbose_name=u"操作时间",auto_now=True)
    pro_type = models.IntegerField(verbose_name=u"操作类别", choices=PROCESS_TYPE,default=0)
    memo = models.CharField(verbose_name="备注",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)

    def get_project_desc(self):
        if self.node:
            return self.node.name
        else:
            return u'启动'

    def get_action_desc(self):
        action_mapping = {0:u'提交',1:u'同意',2:u'拒绝',3:u'终止'}
        # print action_mapping
        if self.pro_type:
            return action_mapping[self.pro_type]
        else:
            return u'提交'

    def get_memo_desc(self):
        if self.memo:
            return self.memo
        else:
            return ''

    def href(self):
        title = u"项目链接"
        return format_html("<a href='/admin/basedata/project/{}/change'>{}</a>",
                           self.project.id, title)


    href.allow_tags = True
    href.short_description = _("项目链接")

    class Meta:
        verbose_name = _("历史事务")
        verbose_name_plural = _("历史事务")
        ordering = ['project','pro_time']


class TodoList(models.Model):
    """

    """
    COTENT_TYPE = (
        (0, u"项目"),
        (1, u"设备更改"),
        (2, u"材料领用"),
        (3, u"设备最终"),
        (4,u"竣工报告"),
        (5,u"工时记录"),
        (6,u"项目经理自评")

    )
    code = models.CharField(_("编码"),max_length=const.DB_CHAR_CODE_10,blank=True,null=True)
    project = models.ForeignKey(Project,verbose_name=_("项目"),on_delete=models.CASCADE)
    user = models.ForeignKey(user_models.Employee,verbose_name=_("操作人"),on_delete=models.CASCADE)
    arrived_time = models.DateTimeField(_("消息时间"), auto_now=True)
    is_read = models.BooleanField(_("已读?"),default=False)
    read_time = models.DateTimeField(_("阅读时间"),blank=True,null=True)
    status = models.BooleanField(_("已完结"),default=False)
    memo = models.CharField(verbose_name=_("备注"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    content_type = models.IntegerField(verbose_name=u"任务类别", choices=COTENT_TYPE,default=0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(TodoList,self).save(force_update,force_update,using,update_fields)
        if not self.code:
            self.code = 'TD%05d' % self.id
            self.save()

    def project_dsc(self):
        if self.project:
            return u'%s'%self.project.workflow_node
        else:
            return u'启动'


    def href(self):
        title = u"链接"

        dict = {1: 'Device_change', 2: 'Material_use', 3: 'Device_final', 4: 'Finish_report', 5: 'work_hour',
                6: 'feedback_report'}
        return format_html("<a href='/admin/basedata/project/{}/change'>{}</a>",
                           self.project.id,title)



    def project_dsc(self):
        return u'%s'%(self.project.name)
    project_dsc.short_description = u'业务流程'

    def start_time(self):
        return self.project.s.strftime('%Y-%m-%d %H:%M')

    href.allow_tags = True
    href.short_description = _("项目链接")

    def submitter(self):
        if self.project.starter.last_name or self.inst.starter.first_name:
            return u"%s%s"%(self.inst.starter.last_name,self.inst.starter.first_name)
        return u"%s"%(self.project.starter.username)
    submitter.short_description = _("submitter")

    class Meta:
        verbose_name = _("待办事务")
        verbose_name_plural = _("待办事务")
        ordering = ['user','-arrived_time']


def get_project(app_label,model_name):
    """

    :param app_label:
    :param model_name:
    :return:
    """
    try:
        return Project.objects.get(app_name=app_label,model_name=model_name)
    except Exception as e:
        return None

