from django.urls import path
from .views import dashboard

app_name = 'receipt'
urlpatterns = [
    path('u/dashboard/building/add', dashboard.BuildingAdd.as_view(), name='building_dashboard_add'),
    path('u/dashboard/building/list', dashboard.BuildingList.as_view(), name='building_dashboard_list'),
]