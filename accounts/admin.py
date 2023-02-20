from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'email',
                'password',
                'image',
                'is_active',
                'is_staff',
                'is_superuser',
            )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name',
                'email',
                'password1',
                'password2',
                'image',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    list_display = (
        'id',
        'name',
        'email',
        'updated_at',
        'created_at',
    )

    list_display_links = ('id', 'name', 'email')
    ordering = ('id',)


admin.site.register(User, UserAdmin)

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import CustomUser
# from django.utils.translation import gettext as _
# from . import models

# class UserAdmin(BaseUserAdmin):
#     ordering = ['id']
#     list_display = ['email']
#     fieldsets = (
#         (None, {'fields': ('img','email', 'password')}),
#         (_('Personal Info'), {'fields': ()}),
#         (
#             _('Permissions'),
#             {
#                 'fields': (
#                     'is_active',
#                     'is_staff',
#                     'is_superuser',
#                 )
#             }
#         ),
#         (_('Important dates'), {'fields': ('last_login',)}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2')
#         }),
#     )

# admin.site.register(models.CustomUser, UserAdmin)
