from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response

# Create your views here.

def site_login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('id_username', '').strip(),
            password= request.POST.get('id_password', ''),
            )
        if user is None:
            messages.error(request, u"密码错误")
        else:
                login(request, user)
                return HttpResponseRedirect(request.GET.get('index', '/'))

    elif request.method == "GET":
        return render(request, "siteHTML/login.html")
