from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class LoginRequiredMixinCustom(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_phonenumber_confirmed:
            return redirect('account:confirm_phonenumber')
        return super().dispatch(request, *args, **kwargs)
