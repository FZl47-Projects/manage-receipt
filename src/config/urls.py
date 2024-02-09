from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('public.urls', namespace='public')),
    path('', include('receipt.urls', namespace='receipt')),
    path('', include('notification.urls', namespace='notification')),
    path('', include('support.urls', namespace='support')),
    path('u/', include('account.urls', namespace='account')),
    path('anything-except-admin/', admin.site.urls),
]

if settings.SERVE_FILE_BY_DJANGO:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'public.views.err_403_handler'
handler404 = 'public.views.err_404_handler'
handler500 = 'public.views.err_500_handler'
