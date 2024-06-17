from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView, ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from core.utils import get_media_url
from core.mixins import views as core_mixins
from receipt.models import Building
from support import forms, models, exports

User = get_user_model()


class QuestionAdd(PermissionRequiredMixin, core_mixins.CreateViewMixin, TemplateView):
    permission_required = ('support.add_question',)
    template_name = 'support/dashboard/question/add.html'
    form = forms.QuestionAddForm

    def get_context_data(self, **kwargs):
        return {
            'buildings': Building.objects.filter(is_active=True)
        }


class QuestionList(PermissionRequiredMixin, core_mixins.TemplateChooserMixin, ListView):
    permission_required = ('support.view_question',)
    paginate_by = 20

    def get_template(self):
        user = self.request.user
        if user.is_admin:
            return 'support/dashboard/question/list.html'
        else:
            return 'support/dashboard/question/user/list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            questions = models.Question.objects.all()
        else:
            # getting questions for the buildings intended for the user
            questions = models.Question.objects.filter(building__buildingavailable__user=user)
        return questions


class QuestionDetail(PermissionRequiredMixin, core_mixins.TemplateChooserMixin, TemplateView):
    permission_required = ('support.view_question',)

    def get_template(self):
        user = self.request.user
        if user.is_admin:
            return 'support/dashboard/question/detail.html'
        else:
            return 'support/dashboard/question/user/detail.html'

    def get_context_data(self, **kwargs):
        question_id = kwargs.get('question_id')
        user = self.request.user
        context = {}
        if user.is_admin:
            context['question'] = get_object_or_404(models.Question, id=question_id)
        else:
            question = get_object_or_404(models.Question, id=question_id, building__buildingavailable__user=user)
            context['answers'] = question.get_answers_by_user(user)
            context['question'] = question
        return context


class QuestionDetailExport(PermissionRequiredMixin, View):
    permission_required = ('support.export_question_data',)

    def get(self, request, question_id):
        question = get_object_or_404(models.Question, id=question_id)
        excel_file = exports.Excel.perform_export_question(question)
        excel_file = get_media_url(excel_file)
        return HttpResponseRedirect(excel_file)


class QuestionDelete(PermissionRequiredMixin, core_mixins.DeleteViewMixin, View):
    permission_required = ('support.delete_answerquestion',)

    def get_object(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id')
        return get_object_or_404(models.Question, id=question_id)


class AnswerDetail(PermissionRequiredMixin, TemplateView):
    permission_required = ('support.view_answerquestion',)
    template_name = 'support/dashboard/answer/detail.html'

    def get_context_data(self, **kwargs):
        answer_id = kwargs.get('answer_id')
        answer = get_object_or_404(models.AnswerQuestion, id=answer_id)
        context = {
            'answer': answer
        }
        return context


class AnswerSubmit(PermissionRequiredMixin, core_mixins.CreateViewMixin, View):
    permission_required = ('support.add_answerquestion',)
    form = forms.AnswerSubmitForm

    def add_additional_data(self, data, obj=None):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(models.Question, id=question_id)
        data['question'] = question
        data['user'] = self.request.user

