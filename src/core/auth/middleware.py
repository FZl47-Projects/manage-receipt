from django.contrib.auth.middleware import MiddlewareMixin
from django.shortcuts import redirect


class UserPhonenumberConfirmed(MiddlewareMixin):
    DASHBOARD_URL = '/d'

    def process_request(self, request):
        if str(request.path).startswith(self.DASHBOARD_URL):
            user = request.user
            if not user.is_authenticated:
                return redirect('account:login_register')
            if not user.is_phonenumber_confirmed:
                return redirect('account:confirm_phonenumber')
