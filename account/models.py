from django.db import models
from review.models import Review
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class UserManager(BaseUserManager):
    def create_user(self,email,password=None):
        if not email:
            raise ValueError('email is must')
        
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using= self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    email = models.EmailField(max_length=50,unique=True)
    name = models.CharField(max_length=255,default='未設定')
    image = models.ImageField(upload_to='profiles',default='profile/default.png')
    updated_at = models.DateTimeField("更新日", auto_now=True) 
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorite_reviews = models.ManyToManyField(Review, related_name='favorite_by',blank=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def display_favorite_reviews(self, obj):
        return ", ".join([review.title for review in obj.favorite_reviews.all()])
    display_favorite_reviews.short_description = 'Favorites Count'

    def __str__(self):
        return self.email       


