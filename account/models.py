from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomBaseUserManager(BaseUserManager):

    def create_user(self, phonenumber, password, email=None, **extra_fields):
        """
        Create and save a user with the given phonenumber and password.
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
        ('normal_user', 'normal_user'),
        ('financial_user', 'financial_user'),
        ('super_user', 'super_user'),
    )

    first_name = models.CharField("first name", max_length=150, blank=True,default="بدون نام")
    username = None
    email = models.EmailField("email address", null=True, blank=True,unique=True)
    phonenumber = PhoneNumberField(region='IR', unique=True)
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

    def __str__(self):
        return f'user - {self.phonenumber}'

    def get_raw_phonenumber(self):
        p = str(self.phonenumber).replace('+98', '')
        return p

    def get_full_name(self):
        fl = f'{self.first_name} {self.last_name}'.strip()
        return fl