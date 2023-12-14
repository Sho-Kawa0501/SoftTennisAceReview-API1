from django.db import models
from django.conf import settings

class Brand(models.Model):
  name = models.CharField(
    max_length=20,
    unique=True,
    blank=False,
    null=False
  )

  def __str__(self):
    return self.name

class Series(models.Model):
  name = models.CharField(
    max_length=50,
    unique=True,
    blank=False,
    null=False
  )
  brand = models.ForeignKey(Brand, on_delete=models.CASCADE,null=False)

  class Meta:
    unique_together = ('name', 'brand')

  def __str__(self):
    return self.name

class Position(models.Model):
  name = models.CharField(
    max_length=30,
    unique=True,
    blank=False,
    null=False,
  )

  def __str__(self):
    return self.name

class Item(models.Model):
  item_name = models.CharField(max_length=30,null=False,db_index=True)
  brand = models.ForeignKey(Brand, on_delete=models.CASCADE,null=False)
  series = models.ForeignKey(Series, on_delete=models.CASCADE,null=False)
  position = models.ForeignKey(Position, on_delete=models.CASCADE,null=False)
  item_photo = models.ImageField(
    blank=True,
    null=True,
    upload_to='items/',
    default='default/default_item.png'
  )
  release_date = models.DateField()
  display = models.BooleanField(default=False)
