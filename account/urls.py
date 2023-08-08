from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('login-register',views.login_register,name='login_register')
]