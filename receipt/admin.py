from django.contrib import admin
from . import models

admin.site.register(models.ReceiptTask)
admin.site.register(models.Receipt)
admin.site.register(models.Building)