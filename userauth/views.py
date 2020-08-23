from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout as logout_user
from django.shortcuts import redirect


def index(request):
    username = ""
    if request.user.is_authenticated:
        username = request.user.username
    return HttpResponse("Placeholder for ddh shiny app. Username: {}".format(username))


class Login(LoginView):
    template_name = 'userauth/Login_form.html'


def logout(request):
    logout_user(request)
    return redirect('login')


def auth(request):
    if request.user.is_authenticated:
        return HttpResponse(status=200)
    return HttpResponse(status=403)
