from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('login-register',views.login_register,name='login_register'),
    # reset password
    path('reset-password',views.reset_password,name='reset_password'),
    path('reset-password/send-code',views.reset_password_send,name='reset_password_send_code'),
    path('reset-password/check-code',views.reset_password_check,name='reset_password_check_code'),
    path('reset-password/set',views.reset_password_set,name='reset_password_set'),
]