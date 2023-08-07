from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from core.models import BaseModel
from core import utils

User = get_user_model()


def upload_receipt_pic_src(instance, path):
    """
        return like this => images/09130009999/...format
    """
    frmt = str(path).split('.')[::-1]
    td = utils.get_time()
    phone_number = instance.user.get_raw_phonenumber()
    return f'images/{phone_number}/{td}/{utils.random_str(8)}.{frmt}'


class Building(BaseModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Receipt(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    amount = models.PositiveBigIntegerField()
    picture = models.ImageField(upload_to=upload_receipt_pic_src)
    is_checked = models.BooleanField(default=False)
    submited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f'#{self.id}'

    def get_score(self):
        raise NotImplementedError
