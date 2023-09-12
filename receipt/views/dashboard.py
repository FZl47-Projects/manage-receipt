from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q, Value, Case, When
from django.db.models.functions import Concat
from django.contrib.auth.mixins import LoginRequiredMixin
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


class BuildingList(View):
    template_name = 'receipt/dashboard/building/list.html'

    @admin_required_cbv()
    def get(self, request):
        context = {
            'buildings': models.Building.objects.all()
        }
        return render(request, self.template_name, context)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        pass


class BuildingDetail(View):
    template_name = 'receipt/dashboard/building/detail.html'

    def get(self, request, building_id):
        context = {
            'building': get_object_or_404(models.Building, id=building_id)
        }
        return render(request, self.template_name, context)


class ReceiptAdd(LoginRequiredMixin, View):
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


class ReceiptList(LoginRequiredMixin, View):

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
            user__phonenumber__icontains=s)
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
            receipts = models.Receipt.objects.all()
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


class ReceiptFinancialUserList(LoginRequiredMixin, View):

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
            user__phonenumber__icontains=s)
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
        return render(request, 'receipt/dashboard/receipt/financial/list.html', context)


class ReceiptDetail(LoginRequiredMixin, View):

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
        data = request.POST
        if role == 'super_user':
            print(data)
        elif role == 'financial_user':
            pass

    @admin_required_cbv()
    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'accepted':
            messages.warning(request, 'عملیات قبلا انجام شده است')
            return redirect(receipt.get_absolute_url())
        self.perform_by_user_role(request, receipt)
        return redirect(receipt.get_absolute_url())


class ReceiptDetailReject(View):

    @admin_required_cbv()
    def post(self, request, receipt_id):
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        # only own user and admin can access
        if receipt.user != user and user.is_admin is False:
            raise Http404
        return redirect(receipt.get_absolute_url())


class ReceiptTaskDetail(View):

    @admin_required_cbv(['super_user'])
    def get(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        context = {
            'receipt_task': receipt_task
        }
        return render(request, 'receipt/dashboard/receipt/financial/detail.html', context)


class ReceiptTaskDetailAccept(View):

    @admin_required_cbv(['super_user'])
    def post(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        if receipt_task.status in ('pending', 'rejected'):
            receipt_task.status = 'accepted'
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
            receipt_task.save()
            messages.success(request, 'عملیات با موفقیت انجام شد')
        else:
            messages.warning(request, 'عملیات قبلا انجام شده است')
        return redirect(receipt_task.get_absolute_url())
