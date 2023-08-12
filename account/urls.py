from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    # login logout and register
    path('login-register',views.login_register,name='login_register'),
    path('logout',views.logout,name='logout'),
    # reset password
    path('reset-password',views.reset_password,name='reset_password'),
    path('reset-password/send-code',views.reset_password_send,name='reset_password_send_code'),
    path('reset-password/check-code',views.reset_password_check,name='reset_password_check_code'),
    path('reset-password/set',views.reset_password_set,name='reset_password_set'),

    # dashboard
    path('dashboard',views.dashboard,name='dashboard'),
    # dashboard operations
    # --- user
    path('dashboard/user/add',views.UserAdd.as_view(),name='user_add'),
    path('dashboard/user/list',views.UserList.as_view(),name='user_list'),
    path('dashboard/user/financial/add',views.UserFinancialAdd.as_view(),name='user_financial_add'),
    path('dashboard/user/financial/list',views.UserFinancialList.as_view(),name='user_financial_list'),
    # --- receipt and building
    path('dashboard/building/add',views.BuildingAdd.as_view(),name='building_add'),
    path('dashboard/building/list',views.BuildingList.as_view(),name='building_list'),
    # --- notification
    path('dashboard/notification/add',views.NotificationAdd.as_view(),name='notification_add'),
    path('dashboard/notification/list',views.NotificationList.as_view(),name='notification_list'),
    path('dashboard/notification/user/add',views.NotificationUserAdd.as_view(),name='notification_user_add'),
    path('dashboard/notification/user/list',views.NotificationUserList.as_view(),name='notification_user_list'),

]