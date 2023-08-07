from core.models import TaskAdmin
from .base import Receipt


class ReceiptTask(TaskAdmin,Receipt):
    
    def perform_checked(self):
        pass
    
    def perform_rejected(self):
        pass

