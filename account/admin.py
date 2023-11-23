from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(UserAdmin):
    def display_favorite_reviews(self, obj):
        return ", ".join([str(review.uuid) for review in obj.favorite_reviews.all()])

    display_favorite_reviews.short_description = 'Favorited Reviews'
    
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
                'favorite_reviews',
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
        'uuid',
        'name',
        'email',
        'updated_at',
        'created_at',
        'display_favorite_reviews',
    )

    list_display_links = ('uuid', 'name', 'email')
    ordering = ('uuid',)

admin.site.register(User, UserAdmin)

