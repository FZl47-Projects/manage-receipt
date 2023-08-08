from django.shortcuts import render


def login_register(request):
    return render(request,'account/login-register.html')