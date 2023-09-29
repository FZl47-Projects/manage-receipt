from django.urls import path
from .views import dashboard

app_name = 'notification'
urlpatterns = [
    path('u/dashboard/notification/add', dashboard.NotificationAdd.as_view(), name='notification_dashboard_add'),
    path('u/dashboard/notification/list', dashboard.NotificationList.as_view(), name='notification_dashboard_list'),
    path('u/dashboard/notification/detail/<int:notification_id>', dashboard.NotificationDetail.as_view(), name='notification_dashboard_detail'),
    path('u/dashboard/notification/delete/<int:notification_id>', dashboard.NotificationDelete.as_view(), name='notification_dashboard_delete'),
    path('u/dashboard/notification/update/<int:notification_id>', dashboard.NotificationUpdate.as_view(), name='notification_dashboard_update'),

    path('u/dashboard/notification/user/add', dashboard.NotificationUserAdd.as_view(), name='notification_dashboard_user_add'),
    path('u/dashboard/notification/user/list', dashboard.NotificationUserList.as_view(), name='notification_dashboard_user_list'),
    path('u/dashboard/notification/user/detail/<int:notification_id>', dashboard.NotificationUserDetail.as_view(), name='notification_dashboard_user_detail'),

    path('u/dashboard/notification/user/personal/list', dashboard.NotificationUserPersonalList.as_view(), name='notification_dashboard_user_personal_list'),
]
