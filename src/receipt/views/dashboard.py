import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q, Value, Case, When, Sum
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import models as permission_models
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import View, TemplateView, ListView
from django.http import Http404
from core.auth.mixins import LoginRequiredMixinCustom
from core.mixins import views as core_mixins
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err, get_media_url, create_form_messages
from receipt import forms, models, exports


class ProjectAdd(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.CreateViewMixin, TemplateView):
    permission_required = ('receipt.add_project',)
    template_name = 'receipt/dashboard/project/add.html'
    form = forms.ProjectAddForm


class ProjectList(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.PermissionObjectsMixin, ListView):
    permission_required = ('receipt.view_project',)
    template_name = 'receipt/dashboard/project/list.html'

    def get_qs_permission(self, *args, **kwargs):
        return {
            'receipt.view_full_project': {
                'name': 'projects',
                'queryset': models.Project.objects.all().distinct()
            },
            'receipt.view_project': {
                'name': 'projects',
                'queryset': models.Project.objects.filter(
                    building__in=self.request.user.get_available_buildings()).distinct()
            },
        }

    def get_queryset(self):
        return self.get_context_perm()['projects']


class ProjectDetail(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.PermissionObjectsMixin,
                    TemplateView):
    permission_required = ('receipt.view_project',)
    template_name = 'receipt/dashboard/project/detail.html'

    def get_qs_permission(self, *args, **kwargs):
        project = kwargs.get('project')
        return {
            'receipt.view_full_building': {
                'name': 'buildings',
                'queryset': project.get_buildings()
            },
            'receipt.view_building': {
                'name': 'buildings',
                'queryset': project.get_buildings().filter(pk__in=self.request.user.get_available_building_ids())
            },
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = kwargs.get('project_id')
        project = get_object_or_404(models.Project, id=project_id)

        context['project'] = project
        context.update(self.get_context_perm(project=project))
        return context


class ProjectUpdate(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.UpdateViewMixin, View):
    permission_required = ('receipt.change_project',)
    form = forms.ProjectUpdateForm

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(models.Project, id=project_id)


class ProjectDelete(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('receipt.delete_project',)

    def get_object(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        return get_object_or_404(models.Project, id=project_id)


class BuildingAdd(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.CreateViewMixin, TemplateView):
    permission_required = ('receipt.add_building',)
    template_name = 'receipt/dashboard/building/add.html'
    form = forms.BuildingAddForm

    def get_context_data(self, **kwargs):
        context = {
            'projects': models.Project.objects.all()
        }
        return context


class BuildingList(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.PermissionObjectsMixin, ListView):
    permission_required = ('receipt.view_building',)
    template_name = 'receipt/dashboard/building/list.html'

    def get_qs_permission(self, *args, **kwargs):
        user = self.request.user
        return {
            'receipt.view_full_building': {
                'name': 'buildings',
                'queryset': models.Building.objects.all()
            },
            'receipt.view_admin_building': {
                'name': 'buildings',
                'queryset': user.get_available_buildings()
            },
            'receipt.view_user_building': {
                'name': 'buildings',
                'queryset': models.Building.get_buildings_user(user)
            },
        }

    def get_queryset(self):
        print(self.get_context_perm())
        return self.get_context_perm().get('buildings', [])


class BuildingDetail(LoginRequiredMixinCustom, PermissionRequiredMixin, TemplateView):
    permission_required = ('receipt.view_building',)
    template_name = 'receipt/dashboard/building/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        building_id = self.kwargs.get('building_id')
        building = self.get_building(building_id)
        # chart data
        user_names = []
        user_payments = []
        for user in building.get_users():
            user_names.append(user.get_full_name())
            user_payments.append(building.get_building_payments_user(user))

        context.update({
            'building': building,
            'projects': models.Project.objects.all(),
            # chart data
            'user_names': json.dumps(user_names),
            'user_payments': json.dumps(user_payments)
        })
        return context

    def get_building(self, building_id):
        user = self.request.user
        building = get_object_or_404(models.Building, id=building_id)
        if not user.has_perm('receipt.view_full_building'):
            if not (building in user.get_available_buildings()):
                raise Http404
        return building


class BuildingDetailExport(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.export_building',)

    def get(self, request, building_id):
        building = get_object_or_404(models.Building, id=building_id)
        excel_file = exports.Excel.perform_export_building(building)
        excel_file = get_media_url(excel_file)
        return HttpResponseRedirect(excel_file)


class BuildingDetailUpdate(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.UpdateViewMixin, View):
    permission_required = ('receipt.change_building',)
    form = forms.BuildingUpdateForm

    def get_object(self):
        building_id = self.kwargs.get('building_id')
        return get_object_or_404(models.Building, id=building_id)


class BuildingDetailDelete(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('receipt.delete_building',)

    def get_object(self, request, *args, **kwargs):
        building_id = kwargs.get('building_id')
        return get_object_or_404(models.Building, id=building_id)


class ReceiptAdd(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.CreateViewMixin,
                 core_mixins.TransactionAtomicViewMixin, TemplateView):
    permission_required = ('receipt.add_receipt',)
    template_name = 'receipt/dashboard/receipt/add.html'
    form = forms.ReceiptAddForm

    def get_context_data(self, **kwargs):
        context = {
            'buildings': self.get_buildings_by_user_perm()
        }
        return context

    def get_buildings_by_user_perm(self):
        user = self.request.user
        if user.has_perm('receipt.view_full_building'):
            return models.Building.objects.filter(is_active=True)
        available_buildings = user.get_available_buildings()
        return models.Building.objects.filter(is_active=True, pk__in=available_buildings)

    def add_additional_data(self, data, obj=None):
        user = self.request.user
        data.setdefault('user', user)

        # check and set status
        data['status'] = 'pending'
        if user.has_perm('receipt.auto_accept_receipt'):
            data['status'] = 'accepted'

    def do_success(self):
        user = self.request.user
        if not user.is_common_admin:
            return
        if user.has_perm('receipt.auto_accept_receipt'):
            return
        # create receipt task admin
        form_data = self.get_data()
        form_data.update({
            'receipt': self.obj,
            'user_admin': self.request.user,
            'receipt_status': 'accepted',
        })
        form_receipt_task = forms.ReceiptTaskAddForm(form_data, self.request.FILES)
        if not form_receipt_task.is_valid():
            create_form_messages(self.request, form_receipt_task)
            self.obj.delete()
        form_receipt_task.save()


class ReceiptList(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.PermissionObjectsMixin, ListView):
    permission_required = ('receipt.view_receipt',)
    template_name = 'receipt/dashboard/receipt/list.html'
    paginate_by = 20

    def sort(self, objects):
        sort_by = self.request.GET.get('sort_by', 'need_to_check')
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

    def search(self, objects):
        s = self.request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('user__first_name', Value(' '), 'user__last_name'))
        amount = s if str(s).isdigit() else 0
        lookup = Q(building__name__icontains=s) | Q(amount=amount) | Q(full_name__icontains=s) | Q(
            user__phonenumber__icontains=s) | Q(tracking_code__icontains=s)
        return objects.filter(lookup)

    def get_qs_permission(self, *args, **kwargs):
        user = self.request.user
        return {
            'receipt.view_full_receipts': {
                'name': 'receipts',
                'queryset': models.Receipt.objects.exclude(receipttask__status__in=['rejected', 'pending'])
            },
            'receipt.view_admin_receipts': {
                'name': 'receipts',
                'queryset': models.Receipt.objects.filter(
                    building__in=user.get_available_buildings()).exclude(
                    receipttask__status__in=['rejected', 'pending'])
            },
            'receipt.view_user_receipts': {
                'name': 'receipts',
                'queryset': user.get_receipts()
            },
            'receipt.view_receipt': {
                'name': 'receipts',
                'queryset': user.get_receipts()
            }
        }

    def get_queryset(self):
        objs = self.get_context_perm().get('receipts', [])
        objs = self.search(objs)
        objs = self.sort(objs)
        return objs


class ReceiptDetail(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.view_receipt',)

    def get(self, request, receipt_id):
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        # only own user and admin and user has perm can access
        if (receipt.user != user) and (user.is_admin is False) and not (
                user.has_perm('receipt.view_full_receipts')):
            raise Http404
        # redirect to receipt task if user is admin or have access and
        # receipt have receipt task and receipt task is pending
        receipt_task = getattr(receipt, 'receipttask', None)
        if receipt_task and receipt_task.status == 'pending' and user.has_perm('receipt.view_admin_receipts'):
            return redirect(receipt_task.get_absolute_url())
        context = {
            'receipt': receipt,
        }
        return render(request, 'receipt/dashboard/receipt/detail.html', context)


class ReceiptDetailUpdate(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.change_receipt',)

    def post(self, request, receipt_id):
        data = request.POST.copy()
        user = request.user
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        task_receipt = getattr(receipt, 'receipttask', None)
        # check user
        if receipt.user != user and not user.has_perm('receipt.change_full_receipt'):
            raise PermissionDenied

        # set default values
        # check access and set ratio score
        if user.has_perm('receipt.set_ratio_score_receipt'):
            data.setdefault('ratio_score', receipt.ratio_score)
        else:
            data['ratio_score'] = receipt.ratio_score
        if receipt_status := data.get('receipt_status', None):
            data['status'] = receipt_status

        form_update_receipt = forms.ReceiptUpdateForm(data=data, instance=receipt, files=request.FILES)
        if form_validate_err(request, form_update_receipt) is False:
            return redirect(receipt.get_absolute_url())

        # user admin can update receipt until task receipt status is pending
        if task_receipt and task_receipt.user_admin == user and task_receipt.status != 'pending':
            raise PermissionDenied

        # update receipt
        form_update_receipt.save()

        # set status task receipt to need to check(if task receipt available and user is who create receipt task)
        """
        # if task_receipt:
        #     if task_receipt.user_admin == user:
        #         # update receipt task
        #         data_task = {
        #             'status': 'pending',
        #             'receipt_status': data.get('receipt_status', None)
        #         }
        #         f = forms.ReceiptTaskUpdateForm(data=data_task, instance=task_receipt)
        #         if f.is_valid():
        #             f.save()
        #     else:
        #         # delete receipt task if user not who create receipt task
        #         task_receipt.delete()
        """

        if task_receipt:
            task_receipt.delete()
        messages.success(request, _('Operation completed successfully'))
        return redirect(receipt.get_absolute_url())


class ReceiptDetailAccept(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.user_accept_receipt',)

    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'accepted':
            messages.warning(request, _('Operation already done'))
            return redirect(receipt.get_absolute_url())
        user = request.user
        data = request.POST.copy()
        # accept receipt
        data['status'] = 'pending'
        if user.has_perm('receipt.set_ratio_score_receipt'):
            data.setdefault('ratio_score', 1)
        else:
            data['ratio_score'] = 1
        if user.is_superuser or user.has_perm('receipt.auto_accept_receipt'):
            data['status'] = 'accepted'
        f = forms.ReceiptAcceptForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        receipt = f.save()
        if not user.is_superuser:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'accepted'
            data['user_admin'] = user
            # set status accept if user has auto accept perm
            if user.has_perm('receipt.auto_accept_receipt_task'):
                data['status'] = 'accepted'

            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, _('Receipt accepted successfully'))
        return redirect(receipt.get_absolute_url())


class ReceiptDetailReject(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.user_reject_receipt',)

    def post(self, request, receipt_id):
        receipt = get_object_or_404(models.Receipt, id=receipt_id)
        if receipt.status == 'rejected':
            messages.warning(request, _('Operation already done'))
            return redirect(receipt.get_absolute_url())
        user = request.user
        data = request.POST.copy()
        # reject receipt
        data['status'] = 'pending'
        if user.is_superuser:
            data['status'] = 'rejected'
        f = forms.ReceiptRejectForm(instance=receipt, data=data)
        if form_validate_err(request, f) is False:
            return redirect(receipt.get_absolute_url())
        f.save()
        if not user.is_superuser:
            # create receipt task
            data['receipt'] = receipt
            data['receipt_status'] = 'rejected'
            data['user_admin'] = user
            f = forms.ReceiptTaskAddForm(data=data)
            if form_validate_err(request, f) is False:
                return redirect(receipt.get_absolute_url())
            f.save()
        messages.success(request, _('Receipt rejected successfully'))
        return redirect(receipt.get_absolute_url())


class ReceiptDetailDelete(LoginRequiredMixinCustom, PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('receipt.delete_receipt',)
    redirect_url = reverse_lazy('receipt:receipt_dashboard_list')

    def get_object(self, request, *args, **kwargs):
        receipt_id = kwargs.get('receipt_id')
        return get_object_or_404(models.Receipt, id=receipt_id)


class ReceiptTaskList(LoginRequiredMixinCustom, PermissionRequiredMixin,
                      core_mixins.TemplateChooserMixin, ListView):
    permission_required = ('receipt.view_receipttask',)
    paginate_by = 20

    def get_template(self):
        user = self.request.user
        if user.has_perm('receipt.view_admin_receipt_task') or user.is_common_admin:
            return 'receipt/dashboard/receipt/task/common_admin/list.html'
        return 'receipt/dashboard/receipt/task/list.html'

    def sort(self, objects):
        sort_by = self.request.GET.get('sort_by', 'latest')
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

    def search(self, objects):
        s = self.request.GET.get('search')
        if not s:
            return objects
        objects = objects.annotate(full_name=Concat('user_admin__first_name', Value(' '), 'user_admin__last_name'))
        amount = s if str(s).isdigit() else 0
        lookup = Q(receipt__building__name__icontains=s) | Q(receipt__amount=amount) | Q(full_name__icontains=s) | Q(
            user_admin__phonenumber__icontains=s) | Q(receipt__tracking_code__icontains=s)
        return objects.filter(lookup)

    def get_queryset(self):
        user = self.request.user
        receipts = models.ReceiptTask.objects.all()
        if not user.has_perm('receipt.view_full_receipts_task'):
            # Get own receipt tasks(admin)
            receipts = receipts.filter(user_admin=user)
        # filter and search
        receipts = self.search(receipts)
        receipts = self.sort(receipts)
        return receipts


class ReceiptTaskDetail(LoginRequiredMixinCustom, PermissionRequiredMixin, TemplateView):
    permission_required = ('receipt.view_receipttask',)
    template_name = 'receipt/dashboard/receipt/task/detail.html'

    def get_context_data(self, **kwargs):
        receipt_task_id = kwargs.get('receipt_task_id')
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        context = {
            'receipt_task': receipt_task
        }
        return context


class ReceiptTaskDetailAccept(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.user_accept_receipt_task',)

    def post(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        if receipt_task.status not in ('pending', 'rejected'):
            messages.warning(request, _('Operation already done'))
            return redirect(receipt_task.get_absolute_url())
        receipt_task.status = 'accepted'
        receipt_task.user_supervisor = request.user
        receipt_task.save()
        messages.success(request, _('Receipt task accepted successfully'))
        return redirect(receipt_task.get_absolute_url())


class ReceiptTaskDetailReject(LoginRequiredMixinCustom, PermissionRequiredMixin, View):
    permission_required = ('receipt.user_reject_receipt_task',)

    def post(self, request, receipt_task_id):
        receipt_task = get_object_or_404(models.ReceiptTask, id=receipt_task_id)
        if receipt_task.status != 'pending':
            messages.warning(request, _('Operation already done'))
            return redirect(receipt_task.get_absolute_url())
        receipt_task.status = 'rejected'
        receipt_task.user_supervisor = request.user
        receipt_task.save()
        messages.success(request, _('Receipt task rejected successfully'))
        return redirect(receipt_task.get_absolute_url())
