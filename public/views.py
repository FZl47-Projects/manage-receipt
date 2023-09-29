from django.shortcuts import render
from notification.models import Notification
from support.models import Question


def err_404_handler(request, exception):
    return render(request, 'public/errors/404.html')


def err_500_handler(request):
    return render(request, 'public/errors/500.html')


def index(request):
    context = {
        'notifications': Notification.objects.filter(is_active=True),
        'questions': Question.objects.all()
    }
    return render(request, 'public/index.html', context)
