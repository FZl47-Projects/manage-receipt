from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from core.auth.decorators import admin_required_cbv
from core.utils import form_validate_err
from support.models import Ticket
from support.forms import TicketForm, TicketFormByAdminForm

User = get_user_model()


class TicketAdd(View):
    template_name = 'support/dashboard/ticket/add.html'

    def get(self, request):
        context = {
            'degrees_of_importance': Ticket.DEGREE_OF_IMPORTANCE_OPTIONS,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        data = request.POST.copy()
        # add user for who created ticket
        data['from_user'] = user
        f = TicketFormByAdminForm if user.is_admin else TicketForm
        f = f(data, request.FILES)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'تیکت پشتیبانی با موفقیت ایجاد شد')
        return redirect('support:support_dashboard_ticket_add')


class TicketListNew(View):
    template_name = 'support/dashboard/ticket/list-new.html'

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', 'importance')
        if sort_by and sort_by != 'importance':
            if sort_by == 'latest':
                objects = objects.order_by('-created_at')
            elif sort_by == 'oldest':
                objects = objects.order_by('created_at')
        return objects

    def get(self, request):
        page_num = request.GET.get('page', 1)
        user = request.user
        # order by time created
        sort_by = request.GET.get('sort_by', 'importance')
        if user.is_admin:
            tickets = Ticket.objects.filter(is_open=True)
        else:
            tickets = user.get_tickets()
        tickets = self.sort(request, tickets)
        pagination = Paginator(tickets, 20)
        pagination = pagination.get_page(page_num)
        tickets = pagination.object_list
        if sort_by == 'importance':
            # default order
            # order tickets by importance
            order_by = ['high', 'medium', 'low']
            tickets = sorted(tickets, key=lambda x: order_by.index(x.degree_of_importance))
        context = {
            'tickets': tickets,
            'pagination': pagination
        }
        return render(request, self.template_name, context)


class TicketListArchive(View):
    template_name = 'support/dashboard/ticket/list-archive.html'

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', None)
        if sort_by:
            if sort_by == 'latest':
                objects = objects.order_by('-created_at')
            elif sort_by == 'oldest':
                objects = objects.order_by('created_at')
        return objects

    def get(self, request):
        page_num = request.GET.get('page', 1)
        user = request.user
        if user.is_admin:
            tickets = Ticket.objects.filter(is_open=False)
        else:
            tickets = user.get_archived_tickets()
        # order by time created
        pagination = Paginator(tickets, 20)
        pagination = pagination.get_page(page_num)
        tickets = pagination.object_list

        context = {
            'tickets': tickets,
            'pagination': pagination
        }
        return render(request, self.template_name, context)
