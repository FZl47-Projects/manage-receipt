from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from core.utils import add_prefix_phonenum
from . import forms


def login_register(request):

    def login_perform(request, data):
        phonenumber = data.get('phonenumber', None)
        password = data.get('password', None)
        if phonenumber and password:
            phonenumber = add_prefix_phonenum(phonenumber)
            user = authenticate(request, username=phonenumber, password=password)
            if user is None:
                messages.error(request, 'کاربری با این مشخصات یافت نشد')
                return redirect('account:login_register')
            login(request, user)
            messages.success(request, 'خوش امدید')
            return redirect('public:home')
        else:
            messages.error(request, 'لطفا فیلد هارا به درستی وارد نمایید')
        return redirect('account:login_register')

    def register_perform(request, data):
        f = forms.RegisterUserForm(data=data)
        if f.is_valid():
            # create user
            user = f.save()
            # login
            login(request, user)
            messages.success(request, 'حساب شما با موفقیت ایجاد شد')
            return redirect('public:home')
        else:
            messages.error(request, 'لطفا فیلد هارا به درستی وارد نمایید')
        return redirect('account:login_register')

    if request.method == 'GET':
        return render(request, 'account/login-register.html')

    elif request.method == 'POST':
        data = request.POST
        type_page = data.get('type-page', 'login')
        if type_page == 'login':
            return login_perform(request, data)
        elif type_page == 'register':
            return register_perform(request, data)
