from django.shortcuts import render
from django.contrib.admin import site
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your views here.
def approve(request,app,model,object_id,operation):
    """

    :param request:
    :param operation:
    :return:
    """
    if operation not in ('1','2','3'):
        messages.warning(request,_("unkown workflow operation"))
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    import datetime
    import copy
    content_type = ContentType.objects.get(app_label=app,model=model)
    obj = content_type.get_object_for_this_type(id=int(object_id))
    title = _("Are you sure?")
    opts = obj._meta
    objects_name = force_text(opts.verbose_name)

    has_workflow = False
    queryset = Modal.objects.filter(content_type=content_type,end__gt=datetime.date.today()).order_by('-end')
    cnt = queryset.count()
    workflow_modal = None
    if cnt > 0:
        workflow_modal = queryset[0]
    else:
        messages.warning(request,_("No workflow model was found"))
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))
    workflow_instance = None
    try:
        workflow_instance = Instance.objects.get(modal = workflow_modal,object_id=object_id)
    except Exception:
        messages.warning(request,_("please start the workflow first"))
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    next_nodes = []
    node_users = []
    is_stop_node = False
    node_has_users = False
    delete_instance = False
    deny_to_first = False
    next_node_description = None
    all_nodes =[x for x in Node.objects.filter(modal=workflow_modal).order_by('-id')]
    current = workflow_instance.current_nodes.all()
    current_tmp = copy.deepcopy(current[0])
    if operation == '4' or operation == '3':
        next_nodes = ['stop']
        is_stop_node = True
    else:
        if current.count() > 1:
            pass
        else:
            tmp_node = current[0]
            if tmp_node.stop or tmp_node == all_nodes[0]:
                next_nodes = ['stop']
                is_stop_node = True
            else:
                if tmp_node.next_node_handler and len(tmp_node.next_node_handler) > 0:
                    hd = tmp_node.next_node_handler
                    klass = NextNodeManager().handlers.get(hd)
                    if klass and isinstance(klass,NextNodeHandler):
                        next_nodes = klass.handle(request,obj,tmp_node)
                        next_node_description = klass.description
                if next_nodes and len(next_nodes) > 0:
                    pass
                elif tmp_node.next and tmp_node.next.count()>0:
                    next_nodes = [nd for nd in tmp_node.next.all()]
                else:
                    position = all_nodes.index(tmp_node)
                    next_nodes = [all_nodes[position-1]]

    if request.POST.get("post"):
        from django.db import transaction
        val = request.POST.getlist(SELECTED_CHECKBOX_NAME)
        memo = request.POST['memo']
        with transaction.atomic():
            try:
                if delete_instance:
                    workflow_instance.delete()
                else:
                    if is_stop_node:
                        workflow_instance.status = 99
                        if operation in ('3', '4'):
                            workflow_instance.status = int(operation)
                        if not workflow_instance.approved_time and operation == '1':
                            workflow_instance.approved_time = datetime.datetime.now()
                        workflow_instance.current_nodes.clear()
                        workflow_instance.save()
                    else:
                        workflow_instance.current_nodes.clear()
                        workflow_instance.current_nodes.add(next_nodes[0])
                        for user in User.objects.filter(id__in=val):
                            todo = TodoList.objects.create(inst=workflow_instance,node=next_nodes[0],user=user,app_name=app,model_name=model)
                        if current_tmp.status_field and current_tmp.status_value:
                            try:
                                setattr(obj,current_tmp.status_field,current_tmp.status_value)
                                obj.save()
                            except Exception as e:
                                pass
                    History.objects.create(inst=workflow_instance,user=request.user,pro_type=int(operation),memo=memo,node=current_tmp)
                    TodoList.objects.filter(inst=workflow_instance,node=current_tmp,status=0).update(status=1)
                messages.success(request,_('workflow approved successfully'))
            except Exception as e:
                messages.error(request,e)
                pass
            if current_tmp.action and len(current_tmp.action) > 0:
                action = WorkflowActionManager().actions.get(current_tmp.action)
                if action and isinstance(action,WorkflowAction):
                    action.action(request,obj,current_tmp,operation)

        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    if len(next_nodes) > 0 and not is_stop_node and operation == '1':
        for node in next_nodes:
            users = compile_node_handler(request,obj,node)
            if len(users) > 0:
                node_has_users = True
            node_users.append({'node':node,'users':users})

    context = dict(
        site.each_context(request),
        title=title,
        opts=opts,
        objects_name=objects_name,
        object=obj,
        operation = operation,
        is_stop_node = is_stop_node,
        delete_instance = delete_instance,
        node_users = node_users,
        node_has_users = node_has_users,
        checkbox_name = SELECTED_CHECKBOX_NAME,
    )
    if next_node_description:
        context.update(dict(next_node_description=next_node_description))
    return TemplateResponse(request,"default/workflow/workflow_approve_confirmation.html",context)