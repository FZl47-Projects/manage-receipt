from django.urls import path
from .views import dashboard

app_name = 'support'
urlpatterns = [
    path('u/dashboard/support/ticket/add', dashboard.TicketAdd.as_view(), name='support_dashboard_ticket_add'),
    path('u/dashboard/support/ticket/list', dashboard.TicketListNew.as_view(), name='support_dashboard_ticket_list_new'),
    path('u/dashboard/support/ticket/list/archive', dashboard.TicketListArchive.as_view(), name='support_dashboard_ticket_list_archive')
]
