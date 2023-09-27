from django.shortcuts import render
from notification.models import Notification


def err_404_handler(request, exception):
    return render(request, 'public/errors/404.html')


def err_500_handler(request):
    return render(request, 'public/errors/500.html')


def index(request):
    context = {
        'notifications': Notification.objects.filter(is_active=True)
    }
    return render(request, 'public/index.html',context)
