from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, Http404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import View, TemplateView, ListView

from receipt.models import Building

from core.mixins import views as core_mixins
from notification import forms, models

User = get_user_model()


class NotificationBuildingAdd(PermissionRequiredMixin, TemplateView):
    permission_required = ('notification.add_notificationuser', 'notification.create_building_notification_user')
    template_name = 'notification/dashboard/add-building-user.html'
    success_message = _('Notifications created successfully')

    def get_context_data(self, **kwargs):
        buildings = None
        user = self.request.user
        if user.is_superuser or user.has_perm('receipt.view_full_building'):
            buildings = Building.objects.filter(is_active=True)
        elif user.has_perm('receipt.view_admin_building'):
            buildings = user.get_available_buildings()
        elif user.has_perm('receipt.view_user_building'):
            buildings = models.Building.get_buildings_user(user)
        return {
            'buildings': buildings
        }

    def post(self, request):
        data = request.POST
        building_id = data.get('building')
        if not building_id:
            raise Http404
        building = get_object_or_404(Building, id=building_id)
        users = building.get_all_users()

        for user in users:
            data_notification = data.copy()
            data_notification['to_user'] = user
            data_notification['type'] = 'CUSTOM_NOTIFICATION'
            f = forms.NotificationUserForm(data=data_notification, files=request.FILES)
            if not f.is_valid():
                continue
            f.save()
        messages.success(request, self.success_message)
        return redirect('notification:notification_building_dashboard_add')


class NotificationAdd(PermissionRequiredMixin, core_mixins.CreateViewMixin, TemplateView):
    permission_required = ('notification.add_notification',)
    template_name = 'notification/dashboard/add.html'
    success_message = _('Notification created successfully')
    form = forms.NotificationForm


class NotificationList(PermissionRequiredMixin, ListView):
    permission_required = ('notification.view_notification',)
    template_name = 'notification/dashboard/list.html'
    paginate_by = 20
    queryset = models.Notification.objects.all()


class NotificationDetail(PermissionRequiredMixin, TemplateView):
    permission_required = ('notification.view_notification',)
    template_name = 'notification/dashboard/detail.html'

    def get_context_data(self, **kwargs):
        notification_id = kwargs.get('notification_id')
        notification = get_object_or_404(models.Notification, id=notification_id)
        context = {
            'notification': notification
        }
        return context


class NotificationDelete(PermissionRequiredMixin, core_mixins.DeleteViewMixin, TemplateView):
    permission_required = ('notification.delete_notification',)
    redirect_url = reverse_lazy('notification:notification_dashboard_list')

    def get_object(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')
        notification = get_object_or_404(models.Notification, id=notification_id)
        return notification


class NotificationUpdate(PermissionRequiredMixin, core_mixins.UpdateViewMixin, View):
    permission_required = ('notification.change_notification',)
    form = forms.NotificationUpdateForm

    def get_object(self):
        notification_id = self.kwargs.get('notification_id')
        return get_object_or_404(models.Notification, id=notification_id)


class NotificationUserAdd(PermissionRequiredMixin, core_mixins.CreateViewMixin, TemplateView):
    permission_required = ('notification.add_notificationuser',)
    template_name = 'notification/dashboard/add-user.html'
    success_message = _('Notification user created successfully')
    form = forms.NotificationUserForm

    def get_context_data(self, **kwargs):
        return {
            'users': User.objects.all()
        }

    def add_additional_data(self, data, obj=None):
        data['type'] = 'CUSTOM_NOTIFICATION'


class NotificationUserList(PermissionRequiredMixin, ListView):
    permission_required = ('notification.view_notificationuser',)
    template_name = 'notification/dashboard/list-user.html'
    paginate_by = 20
    queryset = models.NotificationUser.objects.all()


class NotificationUserPersonalList(ListView):
    template_name = 'notification/dashboard/personal-list.html'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.get_notifications()


class NotificationUserDetail(TemplateView):
    template_name = 'notification/dashboard/detail-user.html'

    def get_context_data(self, **kwargs):
        notification_id = kwargs.get('notification_id')
        notification = get_object_or_404(models.NotificationUser, id=notification_id)
        user = self.request.user
        # only own user and admin can access
        if notification.to_user != user and user.is_admin is False:
            raise Http404
        context = {
            'notification': notification
        }
        return context
