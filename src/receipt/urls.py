from django.urls import path
from .views import dashboard

app_name = 'receipt'
urlpatterns = [

    path('u/dashboard/project/add',dashboard.ProjectAdd.as_view(),name='project_dashboard_add'),
    path('u/dashboard/project/list',dashboard.ProjectList.as_view(),name='project_dashboard_list'),
    path('u/dashboard/project/<int:project_id>',dashboard.ProjectDetail.as_view(),name='project_dashboard_detail'),
    path('u/dashboard/project/<int:project_id>/update',dashboard.ProjectUpdate.as_view(),name='project_dashboard_detail_update'),
    path('u/dashboard/project/<int:project_id>/delete',dashboard.ProjectDelete.as_view(),name='project_dashboard_detail_delete'),


    path('u/dashboard/building/add', dashboard.BuildingAdd.as_view(), name='building_dashboard_add'),
    path('u/dashboard/building/list', dashboard.BuildingList.as_view(), name='building_dashboard_list'),
    path('u/dashboard/building/<int:building_id>', dashboard.BuildingDetail.as_view(),name='building_dashboard_detail'),
    path('u/dashboard/building/<int:building_id>/export', dashboard.BuildingDetailExport.as_view(),name='building_dashboard_detail_export'),
    path('u/dashboard/building/<int:building_id>/update', dashboard.BuildingDetailUpdate.as_view(),name='building_dashboard_detail_update'),
    path('u/dashboard/building/<int:building_id>/delete', dashboard.BuildingDetailDelete.as_view(),name='building_dashboard_detail_delete'),


    path('u/dashboard/receipt/add', dashboard.ReceiptAdd.as_view(), name='receipt_dashboard_add'),
    path('u/dashboard/receipt/list', dashboard.ReceiptList.as_view(), name='receipt_dashboard_list'),

    path('u/dashboard/receipt/<int:receipt_id>', dashboard.ReceiptDetail.as_view(), name='receipt_dashboard_detail'),
    path('u/dashboard/receipt/<int:receipt_id>/update', dashboard.ReceiptDetailUpdate.as_view(), name='receipt_dashboard_detail_update'),
    path('u/dashboard/receipt/<int:receipt_id>/accept', dashboard.ReceiptDetailAccept.as_view(), name='receipt_dashboard_detail_accept'),
    path('u/dashboard/receipt/<int:receipt_id>/reject', dashboard.ReceiptDetailReject.as_view(), name='receipt_dashboard_detail_reject'),
    path('u/dashboard/receipt/<int:receipt_id>/delete', dashboard.ReceiptDetailDelete.as_view(), name='receipt_dashboard_detail_delete'),

    path('u/dashboard/receipt/task/list', dashboard.ReceiptTaskList.as_view(), name='receipt_dashboard_task_list'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>', dashboard.ReceiptTaskDetail.as_view(), name='receipt_dashboard_task_detail'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>/accept', dashboard.ReceiptTaskDetailAccept.as_view(), name='receipt_dashboard_task_detail_accept'),
    path('u/dashboard/receipt/task/<int:receipt_task_id>/reject', dashboard.ReceiptTaskDetailReject.as_view(), name='receipt_dashboard_task_detail_reject'),
]
