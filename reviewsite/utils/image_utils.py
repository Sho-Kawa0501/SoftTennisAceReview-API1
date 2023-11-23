from PIL import Image
from django.core.files.base import ContentFile
import io

# 画像サイズ変更
def resize_image(image, size=(200, 200)):
  img = Image.open(image)
  img.thumbnail(size, Image.ANTIALIAS)
  thumb_io = io.BytesIO()
  img.save(thumb_io, img.format, quality=85)
  image_file = ContentFile(thumb_io.getvalue(), name=image.name)
  return image_file
