from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
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

    def get_form(self, request):
        user_role = request.user.role
        data = request.POST.copy()
        if user_role == 'super_user':
            form = forms.ReceiptAdminAddForm
        elif user_role == 'financial_user':
            # set values
            data['user_admin'] = request.user
            form = forms.ReceiptFinancialAddForm
        else:
            form = forms.ReceiptAddForm
        return form(data, request.FILES)

    def get(self, request):
        context = {
            'buildings': models.Building.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST
        f = self.get_form(request)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'رسید با موفقیت ثبت شد')
        return redirect('receipt:receipt_dashboard_add')
