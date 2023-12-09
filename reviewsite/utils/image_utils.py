from PIL import Image, ExifTags
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

def rotate_image_based_on_exif(image):
  try:
    exif = image._getexif()
    if exif is not None:
      orientation_key = next((key for key, value in ExifTags.TAGS.items() if value == 'Orientation'), None)
      if orientation_key is not None:
        orientation = exif.get(orientation_key)
        if orientation == 3:
          image = image.rotate(180, expand=True)
        elif orientation == 6:
          image = image.rotate(270, expand=True)
        elif orientation == 8:
          image = image.rotate(90, expand=True)
  except (AttributeError, KeyError, IndexError, TypeError):
    pass  # Exif情報がない、または解釈できない場合は何もしない

  return image

# 画像のリサイズ処理
def resize_image(image, size=500):
  image = rotate_image_based_on_exif(image)
  image.thumbnail((size, size))
  new_image = Image.new("RGB", (size, size), (255, 255, 255))
  new_image.paste(image, (int((size - image.size[0]) / 2), int((size - image.size[1]) / 2)))
  return new_image