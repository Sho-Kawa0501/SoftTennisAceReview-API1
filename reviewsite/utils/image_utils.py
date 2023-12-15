from PIL import Image, ExifTags
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


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


def delete_image_from_s3(image_path):
  try:
    s3_client = boto3.client(
      's3',
      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
      region_name=settings.AWS_REGION_NAME
    )
    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=image_path)
  except ClientError as e:
    e
  return None