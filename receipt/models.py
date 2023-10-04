import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from core.models import BaseModel
from core import utils
from core.models import TaskAdmin
from notification.models import NotificationUser
from notification import messages
from account.models import User


def random_str(l=10):
    return utils.random_str(l)


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
    progress_percentage = models.IntegerField(default=0,validators=[MinValueValidator(0), MaxValueValidator(100)])

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

    def get_receipts(self):
        return self.receipt_set.all()

    def get_users(self):
        return User.objects.filter(receipt__building=self).distinct()

    def get_users_sort_by_score(self):
        users = self.get_users()
        for user in users:
            user.score = user.get_score_by_building(self)
        users = list(sorted(users, key=lambda i: i.score,reverse=True))
        return users

    def get_payments(self):
        return self.receipt_set.filter(status='accepted').aggregate(payments=models.Sum('amount'))['payments'] or 0

    def get_building_payments_user(self, user):
        return self.receipt_set.filter(user=user, status='accepted').aggregate(payments=models.Sum('amount'))[
            'payments'] or 0

    def get_building_score_user(self, user):
        receipts = self.receipt_set.filter(user=user, status='accepted')
        score = sum(receipt.get_score() for receipt in receipts)
        return score

    @classmethod
    def get_buildings_user(cls, user):
        return Building.objects.filter(receipt__user=user).distinct()


class BuildingAvailable(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    buildings = models.ManyToManyField('Building')

    def __str__(self):
        return f'building available - {self.user.get_full_name()}'


class ReceiptAbstract(BaseModel):

    STATUS_OPTIONS = (
        ('accepted', 'تایید شده'),
        ('pending', 'در صف'),
        ('rejected', 'رد شده')
    )
    tracking_code = models.CharField(max_length=10,default=random_str)
    status = models.CharField(max_length=15, choices=STATUS_OPTIONS, default='pending')
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    depositor_name = models.CharField(max_length=100)
    deposit_datetime = models.DateTimeField()
    description = models.TextField(null=True, blank=True)  # by user
    note = models.TextField(null=True, blank=True)  # by admin
    amount = models.PositiveBigIntegerField()
    picture = models.ImageField(upload_to=upload_receipt_pic_src, max_length=3000)
    submited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = '-id',

    def get_deposit_datetime(self):
        return self.deposit_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def get_deposit_timepast(self):
        return utils.get_timesince_persian(self.deposit_datetime)


class Receipt(ReceiptAbstract):

    def __str__(self):
        return f'#{self.id} receipt'

    def get_score(self):
        score = 1
        try:
            amount = self.amount
            time_now = utils.get_time(None)
            amount_million = amount / 1_000_000
            days = (time_now - self.deposit_datetime).days or 1
            score = int(days * amount_million) or 1
        except ZeroDivisionError:
            pass
        if score < 0:
            score = 0
        return score

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_detail', args=(self.id,))

    def get_status(self):
        return self.status

    def get_status_label(self):
        return self.get_status_display()


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
            description="""درخواست ثبت فیش تایید شد"""
        )

    def perform_rejected(self):
        NotificationUser.objects.create(
            type='TASK_REJECTED',
            to_user=self.user_admin,
            title=messages.TASK_REJECTED,
            description="""درخواست ثبت فیش رد شد"""
        )

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_task_detail', args=(self.id,))
