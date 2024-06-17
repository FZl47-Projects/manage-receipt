from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
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


class Project(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        permissions = (
            ('view_full_project', _('Can view all projects')),
        )

    def __str__(self):
        return self.name

    def get_buildings(self):
        return self.building_set.all()

    def get_absolute_url(self):
        return reverse('receipt:project_dashboard_detail', args=(self.id,))


class Building(BaseModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        ordering = '-id',

        permissions = (
            ('view_full_building', _('Can view all buildings')),
            ('view_admin_building', _('Can view admin buildings')),
            ('view_user_building', _('Can view user buildings')),
            ('view_financial_building', _('Can view financial part(amount,chart and ..) buildings')),
            ('view_receipts_building', _('Can view receipts buildings')),
            ('view_users_building', _('Can view users buildings')),
            ('view_users_score_building', _('Can view users score buildings')),
            ('export_building', _('Can export all data of buildings')),
        )

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

    def get_all_users(self):
        return User.objects.filter(buildingavailable__buildings__in=[self.id])

    def get_users_sort_by_score(self):
        users = self.get_users()
        for user in users:
            user.score = user.get_scores_by_building(self)
        users = list(sorted(users, key=lambda i: i.score, reverse=True))
        return users

    def get_payments(self):
        return self.receipt_set.filter(status='accepted').exclude(
            receipttask__status__in=['rejected', 'pending']).aggregate(payments=models.Sum('amount'))['payments'] or 0

    def get_building_payments_user(self, user):
        return self.receipt_set.filter(user=user, status='accepted').exclude(
            receipttask__status__in=['rejected', 'pending']).aggregate(payments=models.Sum('amount'))[
            'payments'] or 0

    def get_building_score_user(self, user):
        receipts = self.receipt_set.filter(user=user, status='accepted').exclude(
            receipttask__status__in=['rejected', 'pending'])
        score = sum(receipt.get_score() for receipt in receipts)
        return score

    def get_name_by_flag(self):
        return f'{self.project.name} / {self.name}'

    @classmethod
    def get_buildings_user(cls, user):
        buildings = Building.objects.filter(receipt__user=user).distinct()
        buildings = buildings.annotate(
            payments=models.Sum('receipt__amount')
        )
        return buildings


class BuildingAvailable(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    buildings = models.ManyToManyField('Building')

    class Meta:
        permissions = (
            ('set_available_building', _('Can set available building')),
        )

    def __str__(self):
        return f'building available - {self.user.get_full_name()}'

    @classmethod
    def get_or_create_building_user(cls, user):
        building_available = getattr(user, 'buildingavailable', None)
        if not building_available:
            building_available = BuildingAvailable.objects.create(user=user)
        return building_available


class ReceiptAbstract(BaseModel):
    STATUS_OPTIONS = (
        ('accepted', _('Accepted')),
        ('pending', _('Pending')),
        ('rejected', _('Rejected'))
    )
    tracking_code = models.CharField(max_length=10, default=random_str)
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
    ratio_score = models.FloatField(default=1, validators=[MinValueValidator(0), MaxValueValidator(4)])

    class Meta:
        abstract = True
        ordering = '-id',

    def get_deposit_datetime(self):
        return self.deposit_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def get_deposit_timepast(self):
        return utils.get_timesince_persian(self.deposit_datetime)

    def get_picture_full_url(self):
        try:
            return utils.get_host_url(self.picture.url)
        except AttributeError:
            return ''


class Receipt(ReceiptAbstract):
    class Meta:
        permissions = (
            ('change_full_receipt', _('User can edit all receipt')),
            ('auto_accept_receipt', _('Accept receipt automatically')),
            ('user_accept_receipt', _('User can accept receipt')),
            ('user_reject_receipt', _('User can reject receipt')),
            ('view_full_receipts', _('Can view all receipts')),
            ('view_admin_receipts', _('Can view receipts submited by (admin)')),
            ('view_user_receipts', _('Can view receipts submited by (user)')),
            ('view_ratio_score_receipt', _('Can view ratio score receipt')),
            ('set_ratio_score_receipt', _('Can set ratio score receipt')),
        )

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
        # calc ratio score
        score = score * self.ratio_score
        score = int(score)
        return score

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_detail', args=(self.id,))

    def get_status(self):
        # try:
        #     return self.receipttask.receipt_status
        # except:
        #     return self.status
        return self.status

    def get_status_label(self):
        # try:
        #     # show task receipt status
        #     return self.receipttask.get_receipt_status_display()
        # except:
        #     return self.get_status_display()

        return self.get_status_display()


class ReceiptTask(TaskAdmin):
    class Meta:
        permissions = (
            ('auto_accept_receipt_task', _('Accept receipt task automatically')),
            ('view_full_receipts_task', _('Can view all receipts task')),
            ('view_in_user_detail_receipt_tasks', _('Can access to receipt tasks in user detail page')),
            ('view_admin_receipt_task', _('Can access to receipt tasks user by admin role')),
            ('user_accept_receipt_task', _('User can accept receipt task')),
            ('user_reject_receipt_task', _('User can reject receipt task')),
        )

    RECEIPT_STATUS_OPTIONS = (
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected'))
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
        )

    def perform_rejected(self):
        NotificationUser.objects.create(
            type='TASK_REJECTED',
            to_user=self.user_admin,
            title=messages.TASK_REJECTED,
        )

    def get_absolute_url(self):
        return reverse('receipt:receipt_dashboard_task_detail', args=(self.id,))

    def get_status_receipt_by_admin(self):
        return self.get_receipt_status_display()
