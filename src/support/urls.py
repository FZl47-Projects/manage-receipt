from django.urls import path
from .views import dashboard

app_name = 'support'
urlpatterns = [

    path('u/dashboard/support/question/add', dashboard.QuestionAdd.as_view(), name='support_dashboard_question_add'),
    path('u/dashboard/support/question/list', dashboard.QuestionList.as_view(), name='support_dashboard_question_list'),
    path('u/dashboard/support/question/delete/<int:question_id>', dashboard.QuestionDelete.as_view(), name='support_dashboard_question_delete'),
    path('u/dashboard/support/question/detail/<int:question_id>', dashboard.QuestionDetail.as_view(), name='support_dashboard_question_detail'),
    path('u/dashboard/support/question/detail/<int:question_id>/export', dashboard.QuestionDetailExport.as_view(), name='support_dashboard_question_detail_export'),

    path('u/dashboard/support/answer/detail/<int:answer_id>', dashboard.AnswerDetail.as_view(), name='support_dashboard_answer_detail'),
    path('u/dashboard/support/answer/submit/<int:question_id>', dashboard.AnswerSubmit.as_view(), name='support_dashboard_answer_submit'),
]
