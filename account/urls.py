from django.urls import path
from .views import dashboard

app_name = 'account'
urlpatterns = [
    # login logout and register
    path('login-register', dashboard.login_register, name='login_register'),
    path('logout', dashboard.logout, name='logout'),
    # confirm account
    path('confirm/phonenumber', dashboard.ConfirmPhonenumber.as_view(), name='confirm_phonenumber'),
    path('confirm/phonenumber/check', dashboard.ConfirmPhonenumberCheckCode.as_view(), name='confirm_phonenumber_check_code'),
    # reset password
    path('reset-password', dashboard.reset_password, name='reset_password'),
    path('reset-password/send-code', dashboard.reset_password_send, name='reset_password_send_code'),
    path('reset-password/check-code', dashboard.reset_password_check, name='reset_password_check_code'),
    path('reset-password/set', dashboard.reset_password_set, name='reset_password_set'),

    # dashboard
    path('dashboard', dashboard.Dashboard.as_view(), name='dashboard'),
    path('dashboard/info/detail', dashboard.DashboardInfoDetail.as_view(), name='info_detail'),
    path('dashboard/info/change-password', dashboard.DashboardInfoChangePassword.as_view(), name='info_change_password'),
    # dashboard operations
    # --- user
    path('dashboard/user/update/password', dashboard.UserUpdatePassword.as_view(), name='user_update_password'),
    path('dashboard/user/update', dashboard.UserUpdate.as_view(), name='user_update'),
    path('dashboard/user/add', dashboard.UserAdd.as_view(), name='user_add'),
    path('dashboard/user/list', dashboard.UserList.as_view(), name='user_list'),
    path('dashboard/user/list/component/search', dashboard.UserListComponentPartial.as_view(),
         name='user_list_component_search'),
    path('dashboard/user/task/add', dashboard.UserFinancialAdd.as_view(), name='user_financial_add'),
    path('dashboard/user/task/list', dashboard.UserFinancialList.as_view(), name='user_financial_list'),
    path('dashboard/user/<int:user_id>/detail', dashboard.UserDetail.as_view(), name='user_detail'),
    path('dashboard/user/<int:user_id>/detail/delete', dashboard.UserDetailDelete.as_view(), name='user_detail_delete'),

    path('dashboard/user/<int:user_id>/detail/update/admin', dashboard.UserDetailUpdateByAdmin.as_view(),
         name='user_detail_update_admin'),
]
