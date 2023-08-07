from abc import abstractmethod
from django.db import models
from django.contrib.auth import get_user_model
from .base import BaseModel

User = get_user_model()

class TaskAdmin(BaseModel):

    STATUS_OPTIONS = (
        ('checked','checked'),
        ('pending','pending'),
        ('rejected','rejected')
    )

    # admin user    
    user_admin = models.ForeignKey(User,on_delete=models.CASCADE)
    # super user should be accept or reject admins task
    # when status changed to checked then perform function is called
    status = models.CharField(max_length=15,choices=STATUS_OPTIONS,default='pending')
    description = models.TextField(null=True,blank=True)

    class Meta:
        ordering = '-id',
        abstract = True

    def __str__(self):
        return f'#{self.id} task admin'
    
    @abstractmethod
    def perform_checked(self):
        # must implement by subclassess
        pass

    @abstractmethod
    def perform_rejected(self):
        # must implement by subclassess
        pass
    
    