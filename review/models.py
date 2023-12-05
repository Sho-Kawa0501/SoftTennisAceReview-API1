from django.db import models
from django.conf import settings
from item.models import Item
import uuid


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    title = models.CharField("タイトル", max_length=200)
    image = models.ImageField(upload_to='reviews/', verbose_name='画像', null=True, blank=True)
    content = models.TextField("本文")
    favorites_count = models.IntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    def __str__(self):
        return f"{self.item.item_name} - {self.title}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user','review')


