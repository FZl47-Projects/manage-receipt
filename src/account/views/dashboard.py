import json
import warnings
from django.utils.translation import gettext_lazy as _
from django.http import (JsonResponse, HttpResponseBadRequest, Http404, HttpResponse, HttpResponseRedirect)
from django.contrib import messages
from django.conf import settings
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View, TemplateView, ListView
from django.core import serializers
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import models as permission_models
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import authenticate, login, get_user_model, logout as logout_handler
from core.auth.mixins import LoginRequiredMixinCustom
from core.utils import add_prefix_phonenum, random_num, form_validate_err, get_media_url
from core.auth.decorators import admin_required_cbv
from core import redis_py
from core.mixins import views as core_mixins
from receipt.models import Building, BuildingAvailable, Receipt, ReceiptTask
from notification.models import NotificationUser
from account import forms, exports

User = get_user_model()
RESET_PASSWORD_CONFIG = settings.RESET_PASSWORD_CONFIG
CONFIRM_PHONENUMBER_CONFIG = settings.CONFIRM_PHONENUMBER_CONFIG


class LoginOrRegister(TemplateView):
    template_name = 'account/login-register.html'

    def login_perform(self, data):
        request = self.request
        phonenumber = data.get('phonenumber', None)
        password = data.get('password', None)
        if not (phonenumber or password):
            messages.error(request, _('Please enter fields correctly'))
            return redirect('account:login_register')
        phonenumber = add_prefix_phonenum(phonenumber)
        user = authenticate(request, username=phonenumber, password=password)
        if user is None:
            messages.error(request, _('User not found or account is inactive'))
            return redirect('account:login_register')
        if user.is_active is False:
            messages.error(request, _('Account is inactive'))
            return redirect('account:login_register')
        login(request, user)
        messages.success(request, _('Welcome'))
        # redirect to url or dashboard
        next_url = request.GET.get('next')
        try:
            # maybe next url not valid
            if next_url:
                return redirect(next_url)
        except Exception as e:
            pass
        return redirect('account:dashboard')

    def register_perform(self, data):
        request = self.request
        f = forms.RegisterUserForm(data=data)
        if f.is_valid() is False:
            messages.error(request, _('Please enter fields correctly'))
            return redirect('account:login_register')
        # check for exists user
        phonenumber = f.cleaned_data['phonenumber']
        first_name = f.cleaned_data['first_name']
        last_name = f.cleaned_data['last_name']
        email = f.cleaned_data['email']
        if User.objects.filter(phonenumber=phonenumber).exists() or User.objects.filter(email=email).exists():
            messages.error(request, _('A user has already registered with this number'))
            return redirect('account:login_register')

        # create user
        password = f.cleaned_data['password2']
        user = User(
            phonenumber=phonenumber,
            email=email,
            first_name=first_name,
            last_name=last_name,
            # user must check and active by admin
            is_active=False
        )
        user.set_password(password)
        user.save()
        messages.success(request,
                         _('Your account has been successfully created and will be activated after confirming your mobile number and checking your account'))
        return redirect('account:confirm_phonenumber')

    def post(self, request, *args, **kwargs):
        data = request.POST
        type_page = data.get('type-page', 'login')
        if type_page == 'login':
            return self.login_perform(data)
        elif type_page == 'register':
            return self.register_perform(data)


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
    code = random_num(RESET_PASSWORD_CONFIG['CODE_LENGTH'])
    key = RESET_PASSWORD_CONFIG['STORE_BY'].format(phonenumber)
    # check code state set
    if redis_py.get_value(key) is not None:
        # code is already set
        return HttpResponse(status=409)
    # set code
    redis_py.set_value_expire(key, code, RESET_PASSWORD_CONFIG['TIMEOUT'])
    # send code
    NotificationUser.objects.create(
        type='RESET_PASSWORD_CODE_SENT',
        kwargs={
            'code': code
        },
        to_user=user,
        title=_('Reset password'),
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
    code_stored = redis_py.get_value(key)
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
    code_stored = redis_py.get_value(key)
    if code_stored is None:
        # code is not seted or timeout
        return HttpResponse(status=410)
    if code_stored != code:
        # code is wrong(not same)
        return HttpResponse(status=409)
    user.set_password(password)
    user.save()
    redis_py.remove_key(key)
    NotificationUser.objects.create(
        type='PASSWORD_CHANGED_SUCCESSFULLY',
        to_user=user,
        title=_('Your password changed successfully'),
    )
    return JsonResponse({})


class Dashboard(LoginRequiredMixinCustom, View):

    def get_context_normal_user(self, request, user):
        buildings = Building.get_buildings_user(user)
        # chart data
        building_names = []
        building_payments = []

        for building in buildings:
            building_names.append(building.name)
            building_payments.append(building.get_building_payments_user(user))

        context = {
            'buildings': buildings,
            # chart data
            'building_names': json.dumps(building_names),
            'building_payments': json.dumps(building_payments),
        }
        return context

    def get_context_financial_user(self, request, user):
        buildings = user.get_available_buildings()
        # chart data
        building_names = []
        building_payments = []

        for building in buildings:
            building_names.append(building.name)
            building_payments.append(building.get_payments())

        context = {
            'buildings': buildings,
            'receipts': Receipt.objects.filter(building__in=buildings),
            'users': User.normal_user.all(),
            # chart data
            'building_names': json.dumps(building_names),
            'building_payments': json.dumps(building_payments),
        }
        return context

    def get_context_super_user(self, request, user):
        buildings = Building.objects.all()
        # chart data
        building_names = []
        building_payments = []

        for building in buildings:
            building_names.append(building.name)
            building_payments.append(building.get_payments())

        context = {
            'buildings': buildings,
            'receipts': Receipt.objects.all(),
            'users': User.normal_user.all(),
            'admins': User.financial_user.all(),
            # chart data
            'building_names': json.dumps(building_names),
            'building_payments': json.dumps(building_payments),
        }
        return context

    USER_CONTEXT_NAME = {
        'normal_user': get_context_normal_user,
        'financial_user': get_context_financial_user,
        'super_user': get_context_super_user
    }

    USER_TEMPLATE_NAME = {
        'normal_user': 'account/dashboard/main/user.html',
        'financial_user': 'account/dashboard/main/admin.html',
        'super_user': 'account/dashboard/main/super_admin.html',
    }

    def get_template(self):
        user_role = self.request.user.role
        try:
            return self.USER_TEMPLATE_NAME[user_role]
        except KeyError:
            warnings.warn('template not found for role %s' % user_role)
            raise Http404

    def get_context(self, request):
        # get context by role user
        user = request.user
        user_role = user.role
        try:
            return self.USER_CONTEXT_NAME[user_role](self, request, user)
        except KeyError:
            warnings.warn('context function not found for role %s' % user_role)
            return {}

    def get(self, request):
        context = self.get_context(request)
        return render(request, self.get_template(), context)


class ConfirmPhonenumber(LoginRequiredMixin, View):
    template_name = 'account/confirm-phonenumber.html'

    def get(self, request):
        user = request.user
        if user.is_phonenumber_confirmed:
            return redirect('account:dashboard')
        key = CONFIRM_PHONENUMBER_CONFIG['STORE_BY'].format(user.get_raw_phonenumber())
        context = {
            'code_is_sent': bool(redis_py.get_value(key))
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # AJAX view
        user = request.user
        code = random_num(CONFIRM_PHONENUMBER_CONFIG['CODE_LENGTH'])
        key = CONFIRM_PHONENUMBER_CONFIG['STORE_BY'].format(user.get_raw_phonenumber())
        # check code state set
        if redis_py.get_value(key) is not None:
            # code is already set
            return HttpResponse(status=409)
        # set code
        redis_py.set_value_expire(key, code, CONFIRM_PHONENUMBER_CONFIG['TIMEOUT'])
        # send code
        NotificationUser.objects.create(
            type='CONFIRM_PHONENUMBER_CODE_SENT',
            kwargs={
                'code': code
            },
            to_user=user,
            title=_('Confirm phonenumber'),
            send_notify=True
        )
        return JsonResponse({})


class ConfirmPhonenumberCheckCode(LoginRequiredMixin, View):

    def post(self, request):
        # AJAX view
        data = json.loads(request.body)
        code = data.get('code', None)
        # validate data
        if not code:
            return HttpResponseBadRequest()
        user = request.user
        key = CONFIRM_PHONENUMBER_CONFIG['STORE_BY'].format(user.get_raw_phonenumber())
        # check code
        code_stored = redis_py.get_value(key)
        if code_stored is None:
            # code is not seted or timeout
            return HttpResponse(status=410)
        if code_stored != code:
            # code is wrong(not same)
            return HttpResponse(status=409)
        # confirm phonenumber
        user.is_phonenumber_confirmed = True
        user.save()
        NotificationUser.objects.create(
            type='PHONENUMBER_CONFIRMED',
            to_user=user,
            title=_('Phonenumber confirmed successfully'),
            send_notify=True
        )
        messages.success(request, _('Phonenumber confirmed successfully'))
        return JsonResponse({})


class DashboardInfoDetail(LoginRequiredMixinCustom, TemplateView):
    template_name = 'account/dashboard/information/detail.html'


class DashboardInfoChangePassword(LoginRequiredMixinCustom, TemplateView):
    template_name = 'account/dashboard/information/change-password.html'


class UserAdd(PermissionRequiredMixin, TemplateView):
    permission_required = ('account.add_user',)
    template_name = 'account/dashboard/user/add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buildings'] = Building.objects.filter(is_active=True)
        return context

    def post(self, request):
        data = request.POST.copy()
        f = forms.RegisterUserFullForm(data=data)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        user_visitor = self.request.user
        # create user
        user = f.save(commit=False)
        user.is_active = True
        user.set_password(f.cleaned_data['password2'])
        user.save()
        if user_visitor.has_perm('account.set_available_building'):
            # set building available
            data['user'] = user
            building_available = BuildingAvailable.get_or_create_building_user(user)
            f = forms.SetBuildingAvailableForm(data=data, instance=building_available)
            if f.is_valid():
                f.save()
        # create notif for admin
        NotificationUser.objects.create(
            type='CREATE_USER_BY_ADMIN',
            to_user=request.user,
            title=_('Create an user by the manager'),
            description=_('User %s created successfully') % user.get_raw_phonenumber(),
            is_showing=False
        )
        messages.success(request, _('User account successfully created'))
        return redirect(user.get_absolute_url())


class UserDetail(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.PermissionObjectsMixin, TemplateView):
    permission_required = ('account.view_user',)
    template_name = 'account/dashboard/user/detail.html'

    def get_qs_permission(self, *args, **kwargs):
        user_obj = kwargs.get('user_obj')
        user_visitor = self.get_user_perm()
        return {
            'receipt.view_full_building': {
                'name': 'buildings_user',
                'queryset': Building.get_buildings_user(user_obj)
            },
            'receipt.view_building': {
                'name': 'buildings_user',
                'queryset': Building.get_buildings_user(user_obj).filter(pk__in=user_visitor.get_available_buildings())
            },
            'receipt.view_in_user_detail_receipt_tasks': {
                'name': 'receipt_tasks',
                'queryset': ReceiptTask.objects.filter(user_admin=user_obj)
            },
            'auth.view_group': {
                'name': 'permission_groups',
                'queryset': permission_models.Group.objects.all()
            }
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = kwargs.get('user_id')
        user_obj = get_object_or_404(User, id=user_id)
        if user_obj == self.request.user:
            # user should not have access to self detail
            raise Http404

        context.update(self.get_context_perm(user_obj=user_obj))

        context.update({
            'user_detail': user_obj,  # name 'user_detail' for prevent conflict
            'buildings': Building.objects.filter(is_active=True),
        })

        buildings_user = context.get('buildings_user', [])
        context.update({
            'receipts': user_obj.get_receipts().filter(building__pk__in=buildings_user).exclude(
                receipttask__status__in=['rejected', 'pending'])
        })

        return context


class UserDetailDelete(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('account.delete_user',)

    def do_fail(self):
        messages.error(self.request, _('You cannot delete a super user'))

    def get_object(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        if user.is_super_admin:
            # cant delete super user
            return None
        return user


class UserUpdate(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.UpdateViewMixin, View):
    permission_required = ('account.change_user',)
    form = forms.UpdateUserForm

    def get_object(self):
        return self.request.user


class UserUpdatePassword(LoginRequiredMixinCustom, View):

    def post(self, request):
        user = request.user
        data = request.POST
        f = forms.UpdateUserPasswordForm(data=data)
        if form_validate_err(request, f) is False:
            return redirect('account:info_change_password')
        data = f.cleaned_data
        if not user.check_password(data['current_password']):
            messages.error(request, _('The current password is incorrect'))
            return redirect('account:info_change_password')
        user.set_password(data['new_password'])
        user.save()
        messages.success(request, _('Your password has been updated successfully'))
        return redirect('account:login_register')


class UserList(PermissionRequiredMixin, core_mixins.PermissionObjectsMixin,
               ListView):
    permission_required = ('account.view_user',)
    template_name = 'account/dashboard/user/list.html'
    paginate_by = 20

    def get_qs_permission(self, *args, **kwargs):
        user = self.request.user
        return {
            'account.view_full_user': {
                'name': 'users',
                'queryset': User.objects.get_users()
            },
            'account.view_user': {
                'name': 'users',
                'queryset': User.objects.get_users().filter(
                    buildingavailable__buildings__in=user.get_available_buildings()).distinct()
            },
        }

    def search(self, request, objects):
        s = request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        lookup = Q(phonenumber__icontains=s) | Q(full_name__icontains=s) | Q(
            email__icontains=s)
        return objects.filter(lookup)

    def get_queryset(self):
        return self.get_context_perm()['users']


class UserListExport(PermissionRequiredMixin, View):
    permission_required = ('account.export_list_user',)
    template_name = 'account/dashboard/user/list.html'

    def get(self, request):
        users = User.normal_user.all()
        excel_file = exports.Excel.perform_export_users(users)
        excel_file = get_media_url(excel_file)
        return HttpResponseRedirect(excel_file)


class UserListComponentPartial(PermissionRequiredMixin, core_mixins.PermissionObjectsMixin, ListView):
    permission_required = ('account.view_user',)
    template_name = 'account/dashboard/user/components/list.html'
    paginate_by = 20

    def get_qs_permission(self, *args, **kwargs):
        user = self.request.user
        return {
            'account.view_full_user': {
                'name': 'users',
                'queryset': User.objects.get_users()
            },
            'account.view_user': {
                'name': 'users',
                'queryset': User.objects.get_users().filter(
                    buildingavailable__buildings__in=user.get_available_buildings()).distinct()
            },
        }

    def get_queryset(self):
        return self.get_context_perm()['users']

    @admin_required_cbv()
    def post(self, request):
        # ajax view
        if not request.headers.get('X_REQUESTED_WITH') == 'XMLHttpRequest':
            raise Http404
        data = json.loads(request.body)

        def search(request, objects):
            s = data.get('search')
            if not s:
                return objects
            objects = objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
            lookup = Q(phonenumber__icontains=s) | Q(full_name__icontains=s) | Q(
                email__icontains=s)
            return objects.filter(lookup)

        users = self.get_queryset()
        users = search(request, users)
        users_serialized = serializers.serialize('json', users,
                                                 fields=('id', 'first_name', 'last_name', 'email', 'phonenumber'))
        return JsonResponse(users_serialized, safe=False)


# class UserFinancialAdd(PermissionRequiredMixin, TemplateView):
#     permission_required = ('account.add_user',)
#     template_name = 'account/dashboard/user/add.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['buildings'] = Building.objects.filter(is_active=True)
#         return context
#
#     def post(self, request):
#         data = request.POST.copy()
#         f = forms.RegisterUserFullForm(data=data)
#         if form_validate_err(request, f) is False:
#             return render(request, self.template_name)
#         user_visitor = self.request.user
#         # create user
#         user = f.save(commit=False)
#         user.is_active = True
#         user.set_password(f.cleaned_data['password2'])
#         user.save()
#         if user_visitor.has_perm('account.set_available_building'):
#             # set building available
#             data['user'] = user
#             building_available = BuildingAvailable.get_or_create_building_user(user)
#             f = forms.SetBuildingAvailable(data=data, instance=building_available)
#             if f.is_valid():
#                 f.save()
#         # create notif for admin
#         NotificationUser.objects.create(
#             type='CREATE_USER_BY_ADMIN',
#             to_user=request.user,
#             title=_('Create an user by the manager'),
#             description=_('User %s created successfully') % user.get_raw_phonenumber(),
#             is_showing=False
#         )
#         messages.success(request, _('User account successfully created'))
#         return redirect(user.get_absolute_url())
#
#
# class UserFinancialList(View):
#     template_name = 'account/dashboard/admin/list.html'
#
#     def search(self, request, objects):
#         s = request.GET.get('search')
#         if not s:
#             return objects
#         objects = objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
#         lookup = Q(phonenumber__icontains=s) | Q(full_name__icontains=s) | Q(
#             email__icontains=s)
#         return objects.filter(lookup)
#
#     @admin_required_cbv()
#     def get(self, request):
#         users = User.financial_user.all()
#         users = self.search(request, users)
#         page_num = request.GET.get('page', 1)
#         pagination = Paginator(users, 20)
#         pagination = pagination.get_page(page_num)
#         users = pagination.object_list
#         context = {
#             'users': users,
#             'pagination': pagination
#         }
#         return render(request, self.template_name, context)


class UserDetailUpdateByAdmin(PermissionRequiredMixin, View):
    permission_required = ('account.change_user',)

    def post(self, request, user_id):
        data = request.POST
        user_obj = get_object_or_404(User, id=user_id)
        state_active = user_obj.is_active
        phonenumber = add_prefix_phonenum(data.get('phonenumber', ''))
        # check unique phonenumber(username)
        if phonenumber != user_obj.phonenumber:
            if User.objects.filter(phonenumber=phonenumber).exists():
                messages.error(request, _('A user has already registered with this number'))
                return redirect(user_obj.get_absolute_url())
        f = forms.UserUpdateByAdminForm(data=data, instance=user_obj)
        if form_validate_err(request, f) is False:
            return redirect(user_obj.get_absolute_url())
        user_obj = f.save()
        messages.success(request, _('User updated successfully'))
        if state_active is False and user_obj.is_active:
            # create notif for user
            NotificationUser.objects.create(
                type='USER_ACCOUNT_ACTIVATED',
                to_user=user_obj,
                title=_('Your account has been activated'),
            )
        return redirect(user_obj.get_absolute_url())


class UserBuildingAvailableSet(PermissionRequiredMixin, View):
    permission_required = ('receipt.set_available_building',)

    def post(self, request, user_id):
        data = request.POST
        user_obj = get_object_or_404(User, id=user_id)
        buildings = data.getlist('buildings', [])
        try:
            building_available_obj = user_obj.buildingavailable
        except:
            # Does not exist
            building_available_obj = BuildingAvailable.objects.create(user=user_obj)
        building_available_obj.buildings.set(buildings)
        messages.success(request, _('Setting the building for the user was done successfully'))
        return redirect(user_obj.get_absolute_url())


class UserBuildingAvailableList(PermissionRequiredMixin, View):
    permission_required = ('receipt.set_available_building',)

    def get_available_buildings(self, user_obj):
        admin = self.request.user
        user_buildings = user_obj.get_available_buildings()
        if not admin.is_superuser:
            admin_buildings_ids = admin.get_available_building_ids()
            return user_buildings.filter(pk__in=admin_buildings_ids)
        return user_buildings

    @admin_required_cbv()
    def post(self, request):
        # Ajax view
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            return HttpResponseBadRequest()
        user_obj = get_object_or_404(User, id=user_id)
        buildings_available = self.get_available_buildings(user_obj)
        return JsonResponse(serializers.serialize('json', buildings_available, fields=['id', 'name']), safe=False)


class PermissionGroupsManage(PermissionRequiredMixin, ListView):
    permission_required = ('auth.view_group', 'auth.add_group')
    template_name = 'account/dashboard/permission/manage.html'
    paginate_by = 10
    queryset = permission_models.Group.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = self.get_queryset()
        context['permissions'] = permission_models.Permission.objects.all()
        return context


class PermissionGroupsAdd(PermissionRequiredMixin, core_mixins.CreateViewMixin, View):
    permission_required = ('auth.add_group',)
    form = forms.PermissionGroupCreateForm


class PermissionGroupUpdate(PermissionRequiredMixin, core_mixins.UpdateViewMixin, View):
    permission_required = ('auth.edit_group',)
    form = forms.PermissionGroupUpdateForm

    def get_object(self):
        group_id = self.kwargs.get('group_id')
        return get_object_or_404(permission_models.Group, id=group_id)


class PermissionGroupDelete(PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('auth.delete_group',)

    def get_object(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        return get_object_or_404(permission_models.Group, id=group_id)
