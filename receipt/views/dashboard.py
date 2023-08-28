from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err
from receipt.forms import BuildingForm
from receipt.models import Receipt, Building


class BuildingAdd(View):
    template_name = 'receipt/dashboard/building/add.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        return render(request, self.template_name)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        data = request.POST
        f = BuildingForm(data=data)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'ساختمان با موفقیت ایجاد شد')
        return redirect('receipt:building_dashboard_add')


class BuildingList(View):
    template_name = 'receipt/dashboard/building/list.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        context = {
            'buildings': Building.objects.all()
        }
        return render(request, self.template_name, context)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        pass



class BuildingDetail(View):
    template_name = 'receipt/dashboard/building/detail.html'

    @admin_required_cbv(['super_user'])    
    def get(self,request,building_id):
        context = {
            'building': get_object_or_404(Building,id=building_id)
        }
        return render(request,self.template_name,context)