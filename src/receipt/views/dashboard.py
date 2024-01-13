import json
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q, Value, Case, When, Sum
from django.db.models.functions import Concat
from core.auth.mixins import LoginRequiredMixinCustom
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err, get_media_url
from receipt import forms, models, exports


class ProjectAdd(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/project/add.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        return render(request, self.template_name)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        data = request.POST
        f = forms.ProjectAddForm(data=data)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'پروژه با موفقیت ایجاد شد')
        return redirect('receipt:project_dashboard_add')


class ProjectList(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/project/list.html'

    def get_projects_by_user_role(self, user):
        if user.is_super_admin:
            return models.Project.objects.all()
        elif user.is_common_admin:
            buildings = user.get_available_buildings()
            return models.Project.objects.filter(building__in=buildings)

    @admin_required_cbv()
    def get(self, request):
        context = {
            'projects': self.get_projects_by_user_role(request.user)
        }
        return render(request, self.template_name, context)


class ProjectDetail(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/project/detail.html'

    def get_project_building_by_user_role(self, project, user):
        if user.is_super_admin:
            return project.get_buildings()
        elif user.is_common_admin:
            return project.get_buildings().filter(pk__in=user.get_available_building_ids())

    @admin_required_cbv()
    def get(self, request, project_id):
        project = get_object_or_404(models.Project, id=project_id)
        context = {
            'project': project,
            'buildings': self.get_project_building_by_user_role(project, request.user)
        }
        return render(request, self.template_name, context)


class ProjectUpdate(LoginRequiredMixinCustom, View):

    @admin_required_cbv(['super_user'])
    def post(self, request, project_id):
        project = get_object_or_404(models.Project, id=project_id)
        data = request.POST
        f = forms.ProjectUpdateForm(data=data, instance=project)
        if form_validate_err(request, f) is False:
            return redirect(project.get_absolute_url())
        f.save()
        messages.success(request, 'پروژه با موفقیت بروزرسانی شد')
        return redirect(project.get_absolute_url())


class ProjectDelete(LoginRequiredMixinCustom, View):

    @admin_required_cbv(['super_user'])
    def post(self, request, project_id):
        project = get_object_or_404(models.Project, id=project_id)
        project.delete()
        messages.success(request, 'پروژه با موفقیت حذف شد')
        return redirect('receipt:project_dashboard_list')


class BuildingAdd(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/building/add.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        context = {
            'projects': models.Project.objects.all()
        }
        return render(request, self.template_name, context)

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

    def get_buildings(self):
        user = self.request.user
        if user.is_super_admin:
            return models.Building.objects.all()
        elif user.is_common_admin:
            return user.get_available_buildings()
        else:
            buildings = models.Building.get_buildings_user(user)
            buildings = buildings.annotate(
                payments=Sum('receipt__amount')
            )
            return buildings

    def get(self, request):
        buildings = self.get_buildings()
        context = {
            'buildings': buildings
        }
        return render(request, self.template_name, context)


class BuildingDetail(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/building/detail.html'

    def get_building(self, building_id):
        user = self.request.user
        building = get_object_or_404(models.Building, id=building_id)
        if not user.is_super_admin:
            if not (building in user.get_available_buildings()):
                raise Http404
        return building

    def get(self, request, building_id):
        building = self.get_building(building_id)
        # chart data
        user_names = []
        user_payments = []
        for user in building.get_users():
            user_names.append(user.get_full_name())
            user_payments.append(building.get_building_payments_user(user))

        context = {
            'building': building,
            'projects': models.Project.objects.all(),
            # chart data
            'user_names': json.dumps(user_names),
            'user_payments': json.dumps(user_payments)
        }
        return render(request, self.template_name, context)


class BuildingDetailExport(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/building/detail.html'

    @admin_required_cbv(['super_user'])
    def get(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        excel_file = exports.Excel.perform_export_building(building)
        excel_file = get_media_url(excel_file)
        return HttpResponseRedirect(excel_file)


class BuildingDetailUpdate(LoginRequiredMixinCustom, View):
    template_name = 'receipt/dashboard/building/detail.html'

    @admin_required_cbv(['super_user'])
    def post(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        f = forms.BuildingEditForm(instance=building, data=request.POST)
        if form_validate_err(request, f) is True:
            f.save()
            messages.success(request, 'مشخصات ساختمان با موفقیت بروزرسانی شد')
        return redirect(building.get_absolute_url())


class BuildingDetailDelete(LoginRequiredMixinCustom, View):

    @admin_required_cbv(['super_user'])
    def post(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        building.delete()
        messages.success(request, 'ساختمان با موفقیت حذف شد')
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
        if user_role == 'normal_user':
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
        if user.is_common_admin:
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
        sort_by = request.GET.get('sort_by', 'need_to_check')
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
                When(status="rejected", then=Value(2)),
                When(status="accepted", then=Value(3)),
                default=Value(3)
            )
            )
        elif sort_by == 'datetime_latest':
            objects = objects.order_by('-deposit_datetime')
        elif sort_by == 'datetime_oldest':
            objects = objects.order_by('deposit_datetime')
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

    def get_receipts_by_user_role(self, user):
        if user.is_super_admin:
            return models.Receipt.objects.exclude(receipttask__status__in=['rejected', 'pending'])
        elif user.is_common_admin:
            building = user.get_available_buildings()
            return models.Receipt.objects.filter(building__in=building).exclude(
                receipttask__status__in=['rejected', 'pending'])
        else:
            return user.get_receipts()

    def get_context(self, request):
        user = request.user
        receipts = self.get_receipts_by_user_role(user)
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


class ReceiptTaskList(LoginRequiredMixinCustom, View):

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
        elif sort_by == 'datetime_latest':
            objects = objects.order_by('-receipt__deposit_datetime')
        elif sort_by == 'datetime_oldest':
            objects = objects.order_by('receipt__deposit_datetime')
        return objects

    def search(self, request, objects):
        s = request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('user_admin__first_name', Value(' '), 'user_admin__last_name'))
        amount = s if str(s).isdigit() else 0
        lookup = Q(receipt__building__name__icontains=s) | Q(receipt__amount=amount) | Q(full_name__icontains=s) | Q(
            user_admin__phonenumber__icontains=s) | Q(receipt__tracking_code__icontains=s)
        return objects.filter(lookup)

    def get_pagination(self, request, objects):
        page_num = request.GET.get('page', 1)
        pagination = Paginator(objects, 20)
        pagination = pagination.get_page(page_num)
        objects = pagination.object_list
        return objects, pagination

    def get_context(self, request):
        user = request.user
        receipts = models.ReceiptTask.objects.all()
        if user.is_common_admin:
            # get own receipt tasks
            receipts = receipts.filter(user_admin=user)

        # filter and search
        receipts = self.search(request, receipts)
        receipts = self.sort(request, receipts)
        receipts, pagination = self.get_pagination(request, receipts)
        context = {
            'receipts': receipts,
            'pagination': pagination
        }
        return context

    def get_template(self, request):
        user = request.user
        if user.is_common_admin:
            return 'receipt/dashboard/receipt/task/common_admin/list.html'
        else:
            return 'receipt/dashboard/receipt/task/list.html'

    @admin_required_cbv()
    def get(self, request):
        context = self.get_context(request)
        return render(request, self.get_template(request), context)


class ReceiptDetail(LoginRequiredMixinCustom, View):

    def get(self, request, receipt_id):
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        # only own user and admin can access
        if receipt.user != user and user.is_admin is False:
            raise Http404
        # redirect to receipt task if admin is super admin and
        # receipt have receipt task and receipt task is pending
        receipt_task = getattr(receipt, 'receipttask', None)
        if user.is_admin and receipt_task and receipt_task.status == 'pending':
            return redirect(receipt_task.get_absolute_url())
        context = {
            'receipt': receipt,
        }
        return render(request, 'receipt/dashboard/receipt/detail.html', context)


class ReceiptDetailUpdate(LoginRequiredMixinCustom, View):

    @admin_required_cbv()
    def post(self, request, receipt_id):
        data = request.POST.copy()
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        task_receipt = getattr(receipt, 'receipttask', None)
        # set default values
        data['status'] = data.get('receipt_status', None)
        data.setdefault('ratio_score', receipt.ratio_score)
        f = forms.ReceiptUpdateForm(data=data, instance=receipt)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        # common admin can update receipt until task receipt status is pending
        if user.is_common_admin and task_receipt and task_receipt.status != 'pending':
            raise PermissionDenied
        f.save()
        # set status task receipt to need to check(if task receipt available and user is common admin)
        if task_receipt:
            # update receipt task if user is common admin
            if user.is_common_admin:
                data_task = {
                    'status': 'pending',
                    'receipt_status': data.get('receipt_status', None)
                }
                f = forms.ReceiptTaskUpdateForm(data=data_task, instance=task_receipt)
                if f.is_valid():
                    f.save()
            elif user.is_super_admin:
                # delete receipt task if user is super admin
                task_receipt.delete()
        messages.success(request, 'رسید با موفقیت تغییر کرد')
        return redirect(receipt.get_absolute_url())


class ReceiptDetailAccept(LoginRequiredMixinCustom, View):

    def perform_by_user_role(self, request, receipt):
        user = request.user
        data = request.POST.copy()
        # accept receipt
        data['status'] = 'pending'
        data.setdefault('ratio_score', 1)
        if user.is_super_admin:
            data['status'] = 'accepted'
        f = forms.ReceiptAcceptForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        receipt = f.save()
        if user.is_common_admin:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'accepted'
            data['user_admin'] = user
            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, 'رسید با موفقیت تایید شد')
        # return redirect(receipt.get_absolute_url())
        return redirect('receipt:receipt_dashboard_list')

    @admin_required_cbv()
    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'accepted':
            messages.warning(request, 'عملیات قبلا انجام شده است')
            return redirect(receipt.get_absolute_url())
        return self.perform_by_user_role(request, receipt)


class ReceiptDetailReject(LoginRequiredMixinCustom, View):

    def perform_by_user_role(self, request, receipt):
        user = request.user
        data = request.POST.copy()
        # reject receipt
        data['status'] = 'pending'
        if user.is_super_admin:
            data['status'] = 'rejected'
        f = forms.ReceiptRejectForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        f.save()
        if user.is_common_admin:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'rejected'
            data['user_admin'] = user
            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, 'رسید با موفقیت رد شد')
        # return redirect(receipt.get_absolute_url())
        return redirect('receipt:receipt_dashboard_list')

    @admin_required_cbv()
    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'rejected':
            messages.warning(request, 'عملیات قبلا انجام شده است')
            return redirect(receipt.get_absolute_url())
        return self.perform_by_user_role(request, receipt)


class ReceiptDetailDelete(LoginRequiredMixinCustom, View):

    @admin_required_cbv(['super_user'])
    def get(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        receipt.delete()
        messages.success(request, 'رسید با موفقیت حذف شد')
        return redirect('receipt:receipt_dashboard_list')


class ReceiptTaskDetail(LoginRequiredMixinCustom, View):

    def get_template(self, request):
        user = request.user
        if user.is_common_admin:
            return 'receipt/dashboard/receipt/task/common_admin/detail.html'
        else:
            return 'receipt/dashboard/receipt/task/detail.html'

    @admin_required_cbv()
    def get(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        context = {
            'receipt_task': receipt_task
        }
        return render(request, self.get_template(request), context)


class ReceiptTaskDetailAccept(LoginRequiredMixinCustom, View):

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
        # return redirect(receipt_task.get_absolute_url())
        return redirect('receipt:receipt_dashboard_task_list')


class ReceiptTaskDetailReject(LoginRequiredMixinCustom, View):

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
        # return redirect(receipt_task.get_absolute_url())
        return redirect('receipt:receipt_dashboard_task_list')
