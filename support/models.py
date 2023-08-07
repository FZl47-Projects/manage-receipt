from django.db import models
from core.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model() 

class Ticket(BaseModel):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='from_user')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='to_user')
    title = models.CharField(max_length=150)
    description = models.TextField()
    send_notify = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    

class TicketReplay(Ticket):
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='ticket_replay')
    
    def __str__(self):
        return f'Replay {super().__str__()}'



