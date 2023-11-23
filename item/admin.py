from django.contrib import admin
from .models import Item,Brand,Series,Position

# ブランド、シリーズ、ポジションの管理クラス（必要に応じて追加）
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)

# アイテムの管理クラス
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
  list_display = ('item_name', 'get_brand', 'get_series', 'get_position')

  def get_brand(self, obj):
    return obj.brand.name
  get_brand.short_description = 'ブランド名'

  def get_series(self, obj):
    return obj.series.name
  get_series.short_description = 'シリーズ名'

  def get_position(self, obj):
    return obj.position.name
  get_position.short_description = 'ポジション名'
