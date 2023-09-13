from django.urls import path
from .views import dashboard

app_name = 'receipt'
urlpatterns = [
    path('u/dashboard/building/add', dashboard.BuildingAdd.as_view(), name='building_dashboard_add'),
    path('u/dashboard/building/list', dashboard.BuildingList.as_view(), name='building_dashboard_list'),
    path('u/dashboard/building/<int:building_id>', dashboard.BuildingDetail.as_view(),
         name='building_dashboard_detail'),


    path('u/dashboard/receipt/add', dashboard.ReceiptAdd.as_view(), name='receipt_dashboard_add'),
    path('u/dashboard/receipt/list', dashboard.ReceiptList.as_view(), name='receipt_dashboard_list'),

    path('u/dashboard/receipt/<int:receipt_id>', dashboard.ReceiptDetail.as_view(), name='receipt_dashboard_detail'),
    path('u/dashboard/receipt/<int:receipt_id>/accept', dashboard.ReceiptDetailAccept.as_view(), name='receipt_dashboard_detail_accept'),
    path('u/dashboard/receipt/<int:receipt_id>/reject', dashboard.ReceiptDetailReject.as_view(), name='receipt_dashboard_detail_reject'),
    path('u/dashboard/receipt/<int:receipt_id>/delete', dashboard.ReceiptDetailDelete.as_view(), name='receipt_dashboard_detail_delete'),

    path('u/dashboard/receipt/task/list', dashboard.ReceiptTaskList.as_view(), name='receipt_dashboard_list_financial_user'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>', dashboard.ReceiptTaskDetail.as_view(), name='receipt_dashboard_task_detail'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>/accept', dashboard.ReceiptTaskDetailAccept.as_view(), name='receipt_dashboard_task_detail_accept'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>/reject', dashboard.ReceiptTaskDetailReject.as_view(), name='receipt_dashboard_task_detail_reject'),
]
