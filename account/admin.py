from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = User

    list_display = ('phonenumber','email', 'is_active',
                    'is_staff', 'is_superuser', 'last_login','role')
    list_filter = ('is_active', 'is_staff', 'is_superuser','role')
    fieldsets = (
        (None, {'fields': ('phonenumber','email', 'password','role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phonenumber','email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email','phonenumber')
    ordering = ('email','phonenumber')

admin.site.register(User, CustomUserAdmin)