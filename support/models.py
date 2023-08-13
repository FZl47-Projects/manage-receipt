from django.db import models
from core.models import BaseModel, File
from django.contrib.auth import get_user_model
from core.utils import get_time, random_str

def upload_file_src(instance,path):
    frmt = str(path).split('.')[-1]
    tm = get_time('%Y-%m-%d')
    return f'files/{tm}/{random_str()}.{frmt}'

User = get_user_model() 

class Ticket(BaseModel):

    DEGREE_OF_IMPORTANCE_OPTIONS = (
        ('low','کم'),
        ('medium','متوسط'),
        ('high','زیاد'),
    )

    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='from_user')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='to_user')
    title = models.CharField(max_length=150)
    description = models.TextField()
    send_notify = models.BooleanField(default=True)
    file = models.FileField(upload_to=upload_file_src,null=True,blank=True)
    degree_of_importance = models.CharField(max_length=30,choices=DEGREE_OF_IMPORTANCE_OPTIONS)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def get_degree_of_importance_label(self):
        return self.get_degree_of_importance_display()

class TicketReplay(Ticket):
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='ticket_replay')
    
    
    def __str__(self):
        return f'Replay {super().__str__()}'



