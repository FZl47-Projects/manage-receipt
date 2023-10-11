import os
import xlsxwriter
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from core.auth.decorators import admin_required_cbv
from core.auth.mixins import LoginRequiredMixinCustom
from core.utils import form_validate_err, get_media_url
from receipt.models import Building
from support.models import Ticket, Question, AnswerQuestion
from support.forms import TicketForm, TicketFormByAdminForm, QuestionAddForm

User = get_user_model()


class TicketAdd(View):
    template_name = 'support/dashboard/ticket/add.html'

    def get(self, request):
        context = {
            'degrees_of_importance': Ticket.DEGREE_OF_IMPORTANCE_OPTIONS,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        data = request.POST.copy()
        # add user for who created ticket
        data['from_user'] = user
        f = TicketFormByAdminForm if user.is_admin else TicketForm
        f = f(data, request.FILES)
        if form_validate_err(request, f) is False:
            return render(request, self.template_name)
        f.save()
        messages.success(request, 'تیکت پشتیبانی با موفقیت ایجاد شد')
        return redirect('support:support_dashboard_ticket_add')


class TicketListNew(View):
    template_name = 'support/dashboard/ticket/list-new.html'

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', 'importance')
        if sort_by and sort_by != 'importance':
            if sort_by == 'latest':
                objects = objects.order_by('-created_at')
            elif sort_by == 'oldest':
                objects = objects.order_by('created_at')
        return objects

    def get(self, request):
        page_num = request.GET.get('page', 1)
        user = request.user
        # order by time created
        sort_by = request.GET.get('sort_by', 'importance')
        if user.is_admin:
            tickets = Ticket.objects.filter(is_open=True)
        else:
            tickets = user.get_tickets()
        tickets = self.sort(request, tickets)
        pagination = Paginator(tickets, 20)
        pagination = pagination.get_page(page_num)
        tickets = pagination.object_list
        if sort_by == 'importance':
            # default order
            # order tickets by importance
            order_by = ['high', 'medium', 'low']
            tickets = sorted(tickets, key=lambda x: order_by.index(x.degree_of_importance))
        context = {
            'tickets': tickets,
            'pagination': pagination
        }
        return render(request, self.template_name, context)


class TicketListArchive(View):
    template_name = 'support/dashboard/ticket/list-archive.html'

    def sort(self, request, objects):
        sort_by = request.GET.get('sort_by', None)
        if sort_by:
            if sort_by == 'latest':
                objects = objects.order_by('-created_at')
            elif sort_by == 'oldest':
                objects = objects.order_by('created_at')
        return objects

    def get(self, request):
        page_num = request.GET.get('page', 1)
        user = request.user
        if user.is_admin:
            tickets = Ticket.objects.filter(is_open=False)
        else:
            tickets = user.get_archived_tickets()
        # order by time created
        pagination = Paginator(tickets, 20)
        pagination = pagination.get_page(page_num)
        tickets = pagination.object_list

        context = {
            'tickets': tickets,
            'pagination': pagination
        }
        return render(request, self.template_name, context)


class QuestionAdd(View):
    template_name = 'support/dashboard/question/add.html'

    @admin_required_cbv(['super_user'])
    def get(self, request):
        context = {
            'buildings': Building.objects.all()
        }
        return render(request, self.template_name, context)

    @admin_required_cbv(['super_user'])
    def post(self, request):
        data = request.POST
        f = QuestionAddForm(data, request.FILES)
        if form_validate_err(request, f) is False:
            return redirect('support:support_dashboard_question_add')
        f.save()
        messages.success(request, 'پرسش با موفقیت ایجاد شد')
        return redirect('support:support_dashboard_question_add')


class QuestionList(LoginRequiredMixinCustom, View):

    def get_template_by_user(self, request):
        user = request.user
        if user.is_admin:
            return 'support/dashboard/question/list.html'
        else:
            return 'support/dashboard/question/user/list.html'

    def get_context_by_role(self, request):
        user = request.user
        if user.is_admin:
            questions = Question.objects.all()
        else:
            # getting questions for the buildings intended for the user
            questions = Question.objects.filter(building__buildingavailable__user=user)
        page_num = request.GET.get('page', 1)
        pagination = Paginator(questions, 20)
        pagination = pagination.get_page(page_num)
        questions = pagination.object_list
        context = {
            'questions': questions,
            'pagination': pagination
        }
        return context

    def get(self, request):
        context = self.get_context_by_role(request)
        return render(request, self.get_template_by_user(request), context)


class QuestionDetail(LoginRequiredMixinCustom, View):

    def get_template_by_user(self, request):
        user = request.user
        if user.is_admin:
            return 'support/dashboard/question/detail.html'
        else:
            return 'support/dashboard/question/user/detail.html'

    def get_context_by_user(self, request, question_id):
        user = request.user
        context = {}
        if user.is_admin:
            context['question'] = get_object_or_404(Question, id=question_id)
        else:
            question = get_object_or_404(Question, id=question_id, building__buildingavailable__user=user)
            context['answers'] = question.get_answers_by_user(user)
            context['question'] = question
        return context

    def get(self, request, question_id):
        context = self.get_context_by_user(request, question_id)
        return render(request, self.get_template_by_user(request), context)


class QuestionDetailExport(LoginRequiredMixinCustom, View):

    def perform_export_excel(self, question_obj) -> str:
        file_name = f"{settings.EXPORT_ROOT_DIR}/export-question-{question_obj.title}-{question_obj.building.name}.xlsx"
        export_file = os.path.join(settings.MEDIA_ROOT, file_name)
        workbook = xlsxwriter.Workbook(export_file)
        worksheet = workbook.add_worksheet('اطلاعات')
        # add information
        # add title rows
        worksheet.write(0, 0, 'عنوان پرسش')
        worksheet.write(0, 1, 'نام ساختمان')
        # add data
        worksheet.write(2, 0, question_obj.title)
        worksheet.write(2, 1, question_obj.building.name)
        # add results
        # add title rows
        worksheet = workbook.add_worksheet('نتایج')
        worksheet.write(0, 0, 'مشخصات کاربر')
        worksheet.write(0, 1, 'جواب کاربر')
        row = 2
        # add data
        for answer in question_obj.get_answers():
            # user info
            worksheet.write(row, 0, f"{answer.user.get_full_name()}|{answer.user.get_raw_phonenumber()}")
            # user answer
            worksheet.write(row, 1, answer.answer)
            row += 1
        workbook.close()
        return file_name

    @admin_required_cbv()
    def get(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        excel_file = self.perform_export_excel(question)
        excel_file = get_media_url(excel_file)
        return HttpResponseRedirect(excel_file)


class QuestionDelete(View):

    @admin_required_cbv(['super_user'])
    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        messages.success(request, 'پرسش با موفقیت حذف شد')
        return redirect('support:support_dashboard_question_list')


class AnswerDetail(LoginRequiredMixinCustom, View):
    template_name = 'support/dashboard/answer/detail.html'

    def get(self, request, answer_id):
        answer = get_object_or_404(AnswerQuestion, id=answer_id)
        context = {
            'answer': answer
        }
        return render(request, self.template_name, context)


class AnswerSubmit(LoginRequiredMixinCustom, View):
    template_name = 'support/dashboard/answer/detail.html'

    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        answer = request.POST.get('answer')
        if not answer:
            messages.error(request, 'لطفا پاسخ سوال را به درستی وارد نمایید')
            return redirect(question.get_absolute_url())
        AnswerQuestion.objects.create(
            question=question,
            user=request.user,
            answer=answer,
        )
        messages.success(request, 'پاسخ شما با موفقیت ثبت شد')
        return redirect(question.get_absolute_url())
