"""
    To keep the code clean,
    this views operation is separated from the views file
"""
from django.shortcuts import redirect, reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from core.auth.decorators import admin_required
from core.utils import form_validate_err
from notification.models import NotificationUser
from . import forms

User = get_user_model()


# --- Dashboard ---

@admin_required()
@require_POST
@login_required
def register_user_by_admin(request):
    referer_url = reverse('account:dashboard') + '#users/add'
    data = request.POST
    f = forms.RegisterUserFullForm(data=data)
    if form_validate_err(request,f) is False:
        return redirect(referer_url)
    # create user
    user = f.save()
    # create notif for admin
    NotificationUser.objects.create(
        to_user=request.user,
        description=f"""
            کاربر {user.phonenumber}
            ایجاد شد
        """,
    )
    messages.success(request, 'حساب کاربر با موفقیت ایجاد شد')
    return redirect(referer_url)
