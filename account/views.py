import json
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model, logout as logout_handler
from core.utils import add_prefix_phonenum, random_str, form_validate_err
from core.auth.decorators import admin_required, admin_required_cbv
from core.redis_py import set_value_expire, remove_key, get_value

from notification.models import NotificationUser
from . import forms

User = get_user_model()
RESET_PASSWORD_CONFIG = settings.RESET_PASSWORD_CONFIG


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
        if f.is_valid() is False:
            messages.error(request, 'لطفا فیلد هارا به درستی وارد نمایید')
            return redirect('account:login_register')
        # check for exists normal_user
        phonenumber = f.cleaned_data['phonenumber']
        if User.objects.filter(phonenumber=phonenumber).exists():
            messages.error(request, 'کاربری با این شماره از قبل ثبت شده است')
            return redirect('account:login_register')
        # create user
        password = f.cleaned_data['password2']
        user = User(
            phonenumber=phonenumber,
        )
        user.set_password(password)
        user.save()
        # login
        login(request, user)
        messages.success(request, 'حساب شما با موفقیت ایجاد شد')
        return redirect('public:home')

    if request.method == 'GET':
        return render(request, 'account/login-register.html')

    elif request.method == 'POST':
        data = request.POST
        type_page = data.get('type-page', 'login')
        if type_page == 'login':
            return login_perform(request, data)
        elif type_page == 'register':
            return register_perform(request, data)


def logout(request):
    logout_handler(request)
    return redirect('public:home')


def reset_password(request):
    return render(request, 'account/reset-password.html')


@require_POST
def reset_password_send(request):
    # AJAX view
    data = json.loads(request.body)
    phonenumber = data.get('phonenumber', None)
    # validate data
    if not phonenumber:
        return HttpResponseBadRequest()
    # check user is exists
    try:
        phonenumber = add_prefix_phonenum(phonenumber)
        user = User.objects.get(phonenumber=phonenumber)
    except:
        raise Http404
    code = random_str(RESET_PASSWORD_CONFIG['CODE_LENGTH'])
    key = RESET_PASSWORD_CONFIG['STORE_BY'].format(phonenumber)
    # check code state set
    if get_value(key) is not None:
        # code is already set
        return HttpResponse(status=409)
    # set code
    set_value_expire(key, code, RESET_PASSWORD_CONFIG['TIMEOUT'])
    # send code
    NotificationUser.objects.create(
        to_user=user,
        title='بازیابی رمز عبور',
        description=f"""
             کد بازیابی رمز عبور : 
             {code}
        """,
        send_notify=True
    )
    return JsonResponse({})


@require_POST
def reset_password_check(request):
    # AJAX view
    data = json.loads(request.body)
    phonenumber = data.get('phonenumber', None)
    code = data.get('code', None)
    # validate data
    if (not code) or (not phonenumber):
        return HttpResponseBadRequest()
    phonenumber = add_prefix_phonenum(phonenumber)
    key = RESET_PASSWORD_CONFIG['STORE_BY'].format(phonenumber)
    # check code
    code_stored = get_value(key)
    if code_stored is None:
        # code is not seted or timeout
        return HttpResponse(status=410)
    if code_stored != code:
        # code is wrong(not same)
        return HttpResponse(status=409)
    return JsonResponse({})


@require_POST
def reset_password_set(request):
    # AJAX view
    data = json.loads(request.body)
    f = forms.ResetPasswordSetForm(data)
    # validate data
    if f.is_valid() is False:
        return HttpResponseBadRequest()
    clean_data = f.cleaned_data
    # phonenumber must get from data (not clean_data)
    phonenumber = data['phonenumber']
    code = clean_data['code']
    password = clean_data['password2']
    # check user is exists
    try:
        phonenumber = add_prefix_phonenum(phonenumber)
        user = User.objects.get(phonenumber=phonenumber)
    except:
        raise Http404
    key = RESET_PASSWORD_CONFIG['STORE_BY'].format(phonenumber)
    # check code
    code_stored = get_value(key)
    if code_stored is None:
        # code is not seted or timeout
        return HttpResponse(status=410)
    if code_stored != code:
        # code is wrong(not same)
        return HttpResponse(status=409)
    user.set_password(password)
    user.save()
    remove_key(key)
    NotificationUser.objects.create(
        to_user=user,
        title='رمز عبور شما تغییر کرد',
        description="""
            رمز عبور شما با موفقیت تغییر کرد
        """,
        send_notify=True
    )
    return JsonResponse({})


@login_required
def dashboard(request):

    context = {}
    # get context by role user
    user_role = request.user.role
    if user_role == 'normal_user':
        pass
    elif user_role == 'financial_user':
        pass
    elif user_role == 'super_user':
        context = {
            'users': User.normal_user.all(),
            'financials': User.financial_user.all()
        }

    return render(request, 'account/dashboard/index.html', context)


class UserAdd(View):
    template_name = 'account/dashboard/user/add.html'

    @admin_required_cbv()
    def get(self, request):
        return render(request, self.template_name)

    @admin_required_cbv()
    def post(self, request):
        data = request.POST
        f = forms.RegisterUserFullForm(data=data)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        # create user
        user = f.save()
        # create notif for admin
        NotificationUser.objects.create(
            to_user=request.user,
            title='ایجاد کاربر توسط ادمین',
            description=f"""
                    کاربر {user.phonenumber}
                    ایجاد شد
                """,
            is_showing=False
        )
        messages.success(request, 'حساب کاربر با موفقیت ایجاد شد')
        return redirect('account:user_add')


class UserList(View):
    template_name = 'account/dashboard/user/list.html'

    @admin_required_cbv()
    def get(self, request):
        context = {
            'users': User.normal_user.all()
        }
        return render(request, self.template_name, context)


class UserFinancialAdd(View):
    template_name = 'account/dashboard/admin/add.html'

    @admin_required_cbv()
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        """
            use UserAdd post view
        """
        pass


class UserFinancialList(View):
    template_name = 'account/dashboard/admin/list.html'

    @admin_required_cbv()
    def get(self, request):
        context = {
            'users': User.financial_user.all()
        }
        return render(request, self.template_name, context)
