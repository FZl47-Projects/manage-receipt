from django.db import models
from django.urls import reverse
from core.models import BaseModel, Image
from core.utils import get_time, random_str


def upload_file_src(instance, path):
    frmt = str(path).split('.')[-1]
    tm = get_time('%Y-%m-%d')
    return f'files/{tm}/{random_str()}.{frmt}'


class Ticket(BaseModel):
    DEGREE_OF_IMPORTANCE_OPTIONS = (
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
    )

    from_user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='ticket_from_user')
    to_user = models.ForeignKey('account.User', on_delete=models.CASCADE, null=True, related_name='ticket_to_user')
    title = models.CharField(max_length=150)
    description = models.TextField()
    send_notify = models.BooleanField(default=True)
    file = models.FileField(upload_to=upload_file_src, null=True, blank=True, max_length=300)
    degree_of_importance = models.CharField(max_length=30, choices=DEGREE_OF_IMPORTANCE_OPTIONS)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_degree_of_importance_label(self):
        return self.get_degree_of_importance_display()

    def get_absolute_url(self):
        return '#'


class TicketReplay(Ticket):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticket_replay')

    def __str__(self):
        return f'Replay {super().__str__()}'


class Question(BaseModel, Image):
    title = models.CharField(max_length=150)
    description = models.TextField(null=True)
    building = models.ForeignKey('receipt.Building', on_delete=models.CASCADE, null=True)
    # static options
    option_1 = models.CharField(max_length=100)
    option_2 = models.CharField(max_length=100)
    option_3 = models.CharField(max_length=100)
    option_4 = models.CharField(max_length=100)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return self.title

    def get_answers(self):
        return self.answerquestion_set.all().order_by('user__last_name')

    def get_answers_by_user(self, user):
        return self.get_answers().filter(user=user)

    def get_absolute_url(self):
        return reverse('support:support_dashboard_question_detail', args=(self.id,))

    def get_answer_percentage(self, field_option):
        answers = self.get_answers()
        all_count = answers.count()
        count = answers.filter(answer=field_option).count()
        return (count * 100) / all_count


class AnswerQuestion(BaseModel):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return f'answer - question - {self.question}'

    def get_absolute_url(self):
        return reverse('support:support_dashboard_answer_detail', args=(self.id,))
