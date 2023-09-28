import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import Http404
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Value, Case, When, Sum
from django.db.models.functions import Concat
from core.auth.mixins import LoginRequiredMixinCustom
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err
from receipt import forms, models


class BuildingAdd(View):
    template_name = 'receipt/dashboard/building/add.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        return render(request, self.template_name)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        data = request.POST
        f = forms.BuildingAddForm(data=data)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'ساختمان با موفقیت ایجاد شد')
        return redirect('receipt:building_dashboard_add')


class BuildingList(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/building/list.html'

    def get(self, request):
        user = request.user
        if user.is_admin:
            buildings = models.Building.objects.all()
        else:
            buildings = models.Building.get_buildings_user(user)
            buildings = buildings.annotate(
                payments=Sum('receipt__amount')
            )

        context = {
            'buildings': buildings
        }
        return render(request, self.template_name, context)


class BuildingDetail(View):
    template_name = 'receipt/dashboard/building/detail.html'

    def get(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        # chart data
        user_names = []
        user_payments = []
        for user in building.get_users():
            user_names.append(user.get_full_name())
            user_payments.append(building.get_building_payments_user(user))

        context = {
            'building': building,
            # chart data
            'user_names': json.dumps(user_names),
            'user_payments': json.dumps(user_payments)
        }
        return render(request, self.template_name, context)


class BuildingDetailUpdate(View):
    template_name = 'receipt/dashboard/building/detail.html'

    @admin_required_cbv(['super_user'])
    def post(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        f = forms.BuildingEditForm(instance=building,data=request.POST)
        if form_validate_err(request,f) is True:
            f.save()
            messages.success(request,'مشخصات ساختمان با موفقیت بروزرسانی شد')
        return redirect(building.get_absolute_url())


class BuildingDetailDelete(View):

    @admin_required_cbv(['super_user'])
    def post(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        building.delete()
        messages.success(request,'ساختمان با موفقیت حذف شد')
        return redirect('receipt:building_dashboard_list')


class ReceiptAdd(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/receipt/add.html'

    def get_form_data(self, request):
        user = request.user
        user_role = user.role
        data = request.POST.copy()

        data['status'] = 'pending'
        if user_role == 'super_user':
            data['status'] = 'accepted'
        elif user_role == 'normal_user':
            data['user'] = user
        return data

    def get(self, request):
        context = {
            'buildings': models.Building.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        form_data = self.get_form_data(request)
        form = forms.ReceiptAddForm(form_data, request.FILES)
        if form_validate_err(request, form) is False:
            return redirect('receipt:receipt_dashboard_add')
        receipt = form.save()
        if user.role == 'financial_user':
            form_data['user_admin'] = user
            form_data['receipt'] = receipt
            form_data['receipt_status'] = 'accepted'
            form_receipt_task = forms.ReceiptTaskAddForm(form_data, request.FILES)
            if form_validate_err(request, form_receipt_task) is False:
                return render(request, self.template_name)
            form_receipt_task.save()
        messages.success(request, 'رسید با موفقیت ثبت شد')
        return redirect('receipt:receipt_dashboard_add')


class ReceiptList(LoginRequiredMixinCustom, View):

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', 'latest')
        if sort_by == 'latest':
            objects = objects.order_by('-id')
        elif sort_by == 'oldest':
            objects = objects.order_by('id')
        elif sort_by == 'highest_amount':
            objects = objects.order_by('-amount')
        elif sort_by == 'lowset_amount':
            objects = objects.order_by('amount')
        elif sort_by == 'need_to_check':
            objects = objects.order_by(Case(
                When(status="pending", then=Value(1)),
                When(status="accepted", then=Value(2)),
                When(status="rejected", then=Value(3)),
                default=Value(3)
            )
            )
        return objects

    def search(self, request, objects):
        s = request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('user__first_name', Value(' '), 'user__last_name'))
        amount = s if str(s).isdigit() else 0
        lookup = Q(building__name__icontains=s) | Q(amount=amount) | Q(full_name__icontains=s) | Q(
            user__phonenumber__icontains=s) | Q(tracking_code__icontains=s)
        return objects.filter(lookup)

    def get_pagination(self, request, objects):
        page_num = request.GET.get('page', 1)
        pagination = Paginator(objects, 20)
        pagination = pagination.get_page(page_num)
        objects = pagination.object_list
        return objects, pagination

    def get_context(self, request):
        user = request.user
        if user.is_admin:
            receipts = models.Receipt.objects.exclude(receipttask__status='rejected').exclude(
                receipttask__status='pending')
        else:
            receipts = user.get_receipts()

        # filter and search
        receipts = self.search(request, receipts)
        receipts = self.sort(request, receipts)
        receipts, pagination = self.get_pagination(request, receipts)
        context = {
            'receipts': receipts,
            'pagination': pagination
        }
        return context

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'receipt/dashboard/receipt/list.html', context)


class ReceiptTaskList(View):

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', 'latest')
        if sort_by == 'latest':
            objects = objects.order_by('-id')
        elif sort_by == 'oldest':
            objects = objects.order_by('id')
        elif sort_by == 'highest_amount':
            objects = objects.order_by('-receipt__amount')
        elif sort_by == 'lowset_amount':
            objects = objects.order_by('receipt__amount')
        elif sort_by == 'need_to_check':
            objects = objects.order_by(Case(
                When(status="pending", then=Value(1)),
                When(status="accepted", then=Value(2)),
                When(status="rejected", then=Value(3)),
                default=Value(3)
            )
            )
        return objects

    def search(self, request, objects):
        s = request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('user_admin__first_name', Value(' '), 'user_admin__last_name'))
        amount = s if str(s).isdigit() else 0
        lookup = Q(receipt__building__name__icontains=s) | Q(receipt__amount=amount) | Q(full_name__icontains=s) | Q(
            user_admin__phonenumber__icontains=s) | Q(receipt__tracking_code=s)
        return objects.filter(lookup)

    def get_pagination(self, request, objects):
        page_num = request.GET.get('page', 1)
        pagination = Paginator(objects, 20)
        pagination = pagination.get_page(page_num)
        objects = pagination.object_list
        return objects, pagination

    def get_context(self, request):
        receipts = models.ReceiptTask.objects.all()
        # filter and search
        receipts = self.search(request, receipts)
        receipts = self.sort(request, receipts)
        receipts, pagination = self.get_pagination(request, receipts)
        context = {
            'receipts': receipts,
            'pagination': pagination
        }
        return context

    @admin_required_cbv(['super_user'])
    def get(self, request):
        context = self.get_context(request)
        return render(request, 'receipt/dashboard/receipt/task/list.html', context)


class ReceiptDetail(LoginRequiredMixinCustom, View):

    def get(self, request, receipt_id):
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        # only own user and admin can access
        if receipt.user != user and user.is_admin is False:
            raise Http404

        context = {
            'receipt': receipt
        }
        return render(request, 'receipt/dashboard/receipt/detail.html', context)


class ReceiptDetailAccept(View):

    def perform_by_user_role(self, request, receipt):
        user = request.user
        role = user.role
        data = request.POST.copy()
        # accept receipt
        data['status'] = 'pending'
        if role in settings.SUPER_ADMIN_ROLES:
            data['status'] = 'accepted'
        f = forms.ReceiptAcceptForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        receipt = f.save()
        if role in settings.COMMON_ADMIN_USER_ROLES:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'accepted'
            data['user_admin'] = user
            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, 'رسید با موفقیت تایید شد')
        return redirect(receipt.get_absolute_url())

    @admin_required_cbv()
    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'accepted':
            messages.warning(request, 'عملیات قبلا انجام شده است')
            return redirect(receipt.get_absolute_url())
        return self.perform_by_user_role(request, receipt)


class ReceiptDetailReject(View):

    def perform_by_user_role(self, request, receipt):
        user = request.user
        role = user.role
        data = request.POST.copy()
        # reject receipt
        data['status'] = 'pending'
        if role in settings.SUPER_ADMIN_ROLES:
            data['status'] = 'rejected'
        f = forms.ReceiptRejectForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        f.save()
        if role in settings.COMMON_ADMIN_USER_ROLES:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'rejected'
            data['user_admin'] = user
            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, 'رسید با موفقیت رد شد')
        return redirect(receipt.get_absolute_url())

    @admin_required_cbv()
    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'rejected':
            messages.warning(request, 'عملیات قبلا انجام شده است')
            return redirect(receipt.get_absolute_url())
        return self.perform_by_user_role(request, receipt)


class ReceiptDetailDelete(View):

    @admin_required_cbv(['super_user'])
    def get(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        receipt.delete()
        messages.success(request, 'رسید با موفقیت حذف شد')
        return redirect('receipt:receipt_dashboard_list')


class ReceiptTaskDetail(View):

    @admin_required_cbv(['super_user'])
    def get(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        context = {
            'receipt_task': receipt_task
        }
        return render(request, 'receipt/dashboard/receipt/task/detail.html', context)


class ReceiptTaskDetailAccept(View):

    @admin_required_cbv(['super_user'])
    def post(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        if receipt_task.status in ('pending', 'rejected'):
            receipt_task.status = 'accepted'
            receipt_task.user_super_admin = request.user
            receipt_task.save()
            messages.success(request, 'رسید با موفقیت تایید شد')
        else:
            messages.warning(request, 'عملیات قبلا انجام شده است')
        return redirect(receipt_task.get_absolute_url())


class ReceiptTaskDetailReject(View):

    @admin_required_cbv(['super_user'])
    def post(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        if receipt_task.status == 'pending':
            receipt_task.status = 'rejected'
            receipt_task.user_super_admin = request.user
            receipt_task.save()
            messages.success(request, 'عملیات با موفقیت انجام شد')
        else:
            messages.warning(request, 'عملیات قبلا انجام شده است')
        return redirect(receipt_task.get_absolute_url())
