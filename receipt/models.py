from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import BaseModel
from core import utils
from core.models import TaskAdmin
from notification.models import NotificationUser
from notification import messages

User = get_user_model()


def upload_receipt_pic_src(instance, path):
    """
        return like this => images/09130009999/.. .format
    """
    frmt = str(path).split('.')[::-1]
    td = utils.get_time()
    phone_number = instance.user.get_raw_phonenumber()
    return f'images/{phone_number}/{td}/{utils.random_str(8)}.{frmt}'


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
    
    def get_dashboard_absolute_url(self):
        return reverse('receipt:building_dashboard_detail',args=(self.id,))
    


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


class ReceiptTask(TaskAdmin, Receipt):

    def perform_checked(self):
        Receipt.objects.create(
            user=self.user,
            building=self.building,
            name=self.name,
            description=self.description,
            amount=self.amount,
            picture=self.picture,
            is_checked=self.is_checked,
            submited_at=self.submited_at
        )

    def perform_rejected(self):
        NotificationUser(
            to_user=self.user_admin,
            title=messages.TASK_REJECTED,
            description="""
                درخواست ثبت فیش رد شد
            """
        )
