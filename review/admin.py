from django.contrib import admin
from review import models

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_item_name', 'user', 'created_at', 'updated_at')
    list_filter = ('item', 'user')

    def get_item_name(self, obj):
        return obj.item.item_name
    get_item_name.short_description = 'アイテム名'

admin.site.register(models.Favorite)

@admin.register(models.UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'get_item_name', 'get_review_title')

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'ユーザーのメールアドレス'

    def get_item_name(self, obj):
        return obj.review.item.item_name
    get_item_name.short_description = 'アイテム名'

    def get_review_title(self, obj):
        return obj.review.title
    get_review_title.short_description = 'レビュータイトル'
