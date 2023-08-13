from django.urls import path
from .views import dashboard

app_name = 'notification'
urlpatterns = [
    path('u/dashboard/notification/add', dashboard.NotificationAdd.as_view(), name='notification_dashboard_add'),
    path('u/dashboard/notification/list', dashboard.NotificationList.as_view(), name='notification_dashboard_list'),
    path('u/dashboard/notification/user/add', dashboard.NotificationUserAdd.as_view(), name='notification_dashboard_user_add'),
    path('u/dashboard/notification/user/list', dashboard.NotificationUserList.as_view(), name='notification_dashboard_user_list'),
]
