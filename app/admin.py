from django.contrib import admin
from app import models
from django.contrib.admin import ModelAdmin

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_item_name', 'user', 'created_at', 'updated_at')
    list_filter = ('item', 'user')

    def get_item_name(self, obj):
        return obj.item.item_name
    get_item_name.short_description = 'アイテム名'

admin.site.register(models.Favorite)