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
    path('dashboard',views.Dashboard.as_view(),name='dashboard'),
    path('dashboard/info/detail',views.DashboardInfoDetail.as_view(),name='info_detail'),
    # dashboard operations
    # --- user
    path('dashboard/user/update',views.UserUpdate.as_view(),name='user_update'),
    path('dashboard/user/add',views.UserAdd.as_view(),name='user_add'),
    path('dashboard/user/list',views.UserList.as_view(),name='user_list'),
    path('dashboard/user/task/add',views.UserFinancialAdd.as_view(),name='user_financial_add'),
    path('dashboard/user/task/list',views.UserFinancialList.as_view(),name='user_financial_list'),
]