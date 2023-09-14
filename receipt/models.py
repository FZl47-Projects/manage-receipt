import datetime
from django.db import models
from django.urls import reverse
from core.models import BaseModel
from core import utils
from core.models import TaskAdmin
from notification.models import NotificationUser
from notification import messages


def upload_receipt_pic_src(instance, path):
    frmt = str(path).split('.')[-1]
    td = utils.get_time('%Y-%m-%d')
    phone_number = instance.user.get_raw_phonenumber()
    return f'images/users/{phone_number}/{td}/{utils.random_str(8)}.{frmt}'


class Building(BaseModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    progress_percentage = models.IntegerField(default=0)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return self.name

    @property
    def progress_percentage_label(self):
        p = self.progress_percentage
        if 35 < p < 65:
            return 'half'
        elif p < 50:
            return 'below_half'
        elif p > 50:
            return 'above_half'

    def get_absolute_url(self):
        return reverse('receipt:building_dashboard_detail', args=(self.id,))


class ReceiptAbstract(BaseModel):
    STATUS_OPTIONS = (
        ('accepted', 'تایید شده'),
        ('pending', 'در صف'),
        ('rejected', 'رد شده')
    )
    status = models.CharField(max_length=15, choices=STATUS_OPTIONS, default='pending')
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)  # by user
    note = models.TextField(null=True, blank=True)  # by admin
    amount = models.PositiveBigIntegerField()
    picture = models.ImageField(upload_to=upload_receipt_pic_src, max_length=3000)
    submited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Receipt(ReceiptAbstract):

    def __str__(self):
        return f'#{self.id} receipt'

    def get_score(self):
        score = 1
        try:
            amount = self.amount
            time_now = utils.get_time(None)
            amount_million = amount / 1_000_000
            days = (time_now - self.submited_at).days or 1
            score = int(days * amount_million) or 1
        except ZeroDivisionError:
            pass
        return score

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_detail', args=(self.id,))

    def get_status(self):
        return self.status


class ReceiptTask(TaskAdmin):
    RECEIPT_STATUS_OPTIONS = (
        ('accepted', 'تایید شده'),
        ('rejected', 'رد شده')
    )
    receipt_status = models.CharField(max_length=15, choices=RECEIPT_STATUS_OPTIONS, default='accepted')
    receipt = models.OneToOneField('Receipt', on_delete=models.CASCADE)

    def perform_checked(self):
        self.receipt.status = self.receipt_status
        self.receipt.save()
        NotificationUser.objects.create(
            type='TASK_ACCEPTED',
            to_user=self.user_admin,
            title=messages.TASK_ACCEPTED,
            description="""
                    درخواست ثبت فیش تایید شد
            """
        )

    def perform_rejected(self):
        NotificationUser.objects.create(
            type='TASK_REJECTED',
            to_user=self.user_admin,
            title=messages.TASK_REJECTED,
            description="""
                درخواست ثبت فیش رد شد
            """
        )

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_task_detail', args=(self.id,))
