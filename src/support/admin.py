from django.contrib import admin
from . import models

admin.site.register(models.Ticket)
admin.site.register(models.TicketReplay)
admin.site.register(models.Question)
admin.site.register(models.AnswerQuestion)