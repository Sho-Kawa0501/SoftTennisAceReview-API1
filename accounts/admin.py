from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser
from django.utils.translation import gettext as _
from . import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email']
    fieldsets = (
        (None, {'fields': ('img','email', 'password')}),
        (_('Personal Info'), {'fields': ()}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

admin.site.register(models.CustomUser, UserAdmin)

