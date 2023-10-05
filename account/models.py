from django.db import models
from django.urls import reverse
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from support.models import Ticket


class CustomBaseUserManager(BaseUserManager):

    def create_user(self, phonenumber, password, email=None, **extra_fields):
        """
        Create and save a normal_user with the given phonenumber and password.
        """
        if not phonenumber:
            raise ValueError("The phonenumber must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, phonenumber=phonenumber, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_financial_user(self, phonenumber, password, email=None, **extra_fields):
        return self.create_user(phonenumber=phonenumber, password=password, role='financial_user', email=email,
                                **extra_fields)

    def create_superuser(self, phonenumber, password, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields['is_phonenumber_confirmed'] = True

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phonenumber=phonenumber, password=password, role='super_user', email=email,
                                **extra_fields)


class NormalUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role='normal_user')


class FinancialUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role='financial_user')


class SuperUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role='super_user')


class User(AbstractUser):
    ROLE_USER_OPTIONS = (
        ('normal_user', 'کاربر عادی'),
        ('financial_user', 'ادمین مالی'),
        ('super_user', 'ادمین وِیژه'),
    )

    first_name = models.CharField("first name", max_length=150, blank=True, default="بدون نام")
    username = None
    email = models.EmailField("email address", null=True, blank=True, unique=True)
    phonenumber = PhoneNumberField(region='IR', unique=True)
    is_phonenumber_confirmed = models.BooleanField(default=False)
    # type users|roles
    role = models.CharField(max_length=20, choices=ROLE_USER_OPTIONS, default='normal_user')

    USERNAME_FIELD = "phonenumber"
    REQUIRED_FIELDS = []

    objects = CustomBaseUserManager()
    normal_user = NormalUserManager()
    financial_user = FinancialUserManager()
    super_user = SuperUserManager()

    class Meta:
        ordering = '-id',

    @property
    def is_admin(self):
        return True if self.role in settings.ADMIN_USER_ROLES else False

    @property
    def is_common_admin(self):
        return True if self.role in settings.COMMON_ADMIN_USER_ROLES else False

    @property
    def is_super_admin(self):
        return True if self.role in settings.SUPER_ADMIN_ROLES else False

    def __str__(self):
        return f'{self.role} - {self.phonenumber}'

    def get_role_label(self):
        return self.get_role_display()

    def get_raw_phonenumber(self):
        p = str(self.phonenumber).replace('+98', '')
        return p

    def get_full_name(self):
        fl = f'{self.first_name} {self.last_name}'.strip() or 'بدون نام'
        return fl

    def get_email(self):
        return self.email or '-'

    def get_image_url(self):
        return '/static/images/dashboard/client_img.png'

    def get_last_login(self):
        if self.last_login:
            return self.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return '-'

    def get_receipts(self):
        return self.receipt_set.all()

    def get_accepted_receipts(self):
        return self.get_receipts().filter(status='accepted')

    def get_last_receipt(self):
        return self.get_receipts().first()

    def get_tickets(self):
        return Ticket.objects.filter(to_user=self)

    def get_archived_tickets(self):
        return Ticket.objects.filter(to_user=self, is_open=False)

    def get_notifications(self):
        return self.notificationuser_set.all()

    def get_scores_by_building(self, building):
        receipts = self.receipt_set.filter(building=building, status='accepted').distinct()
        score = 0
        for receipt in receipts:
            score += receipt.get_score()
        return score

    def get_scores(self):
        receipts = self.receipt_set.filter(status='accepted').distinct()
        score = 0
        for receipt in receipts:
            score += receipt.get_score()
        return score

    def get_absolute_url(self):
        return reverse('account:user_detail', args=(self.id,))

    def get_payments(self):
        return self.receipt_set.filter(status='accepted').aggregate(payments=models.Sum('amount'))['payments'] or 0

    def get_available_buildings(self):
        try:
            return self.buildingavailable.buildings.all()
        except:
            return []

    def get_available_building_ids(self):
        try:
            return self.buildingavailable.buildings.values_list('id',flat=True)
        except:
            return []
        