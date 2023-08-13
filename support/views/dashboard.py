from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err
from support.models import Ticket
from support.forms import TicketForm

User = get_user_model()


class TicketAdd(View):
    template_name = 'support/dashboard/ticket/add.html'

    @admin_required_cbv()
    def get(self, request):
        context = {
            'degrees_of_importance': Ticket.DEGREE_OF_IMPORTANCE_OPTIONS,
            'users': User.objects.all()
        }
        return render(request, self.template_name, context)

    @admin_required_cbv()
    def post(self, request):
        data = request.POST.copy()
        # add this admin for who created ticket
        data['from_user'] = request.user
        f = TicketForm(data, request.FILES)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'تیکت پشتیبانی با موفقیت ایجاد شد')
        return redirect('support:support_dashboard_ticket_add')


class TicketListNew(View):
    template_name = 'support/dashboard/ticket/list-new.html'

    @admin_required_cbv()
    def get(self, request):
        page_num = request.GET.get('page', 1)
        tickets = Ticket.objects.filter(is_open=True)
        pagination = Paginator(tickets, 40)
        pagination = pagination.get_page(page_num)
        tickets = pagination.object_list
        # order tickets
        order_by = ['high', 'medium', 'low']
        tickets = sorted(tickets, key=lambda x: order_by.index(x.degree_of_importance))
        context = {
            'tickets': tickets,
            'pagination': pagination
        }
        return render(request, self.template_name, context)

    @admin_required_cbv()
    def post(self, request):
        pass
