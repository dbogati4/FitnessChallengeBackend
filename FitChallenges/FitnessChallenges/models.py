from django.db import models

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    user_name = models.CharField(max_length=500)
    email_address = models.EmailField(unique=True)
    password = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.BigIntegerField(null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    smoke_habits = models.CharField(max_length=35, null=True)  
    alcohol_habits = models.CharField(max_length=35, null=True)
    gender = models.CharField(max_length=30, null=True)
    verified = models.CharField(null=True, default=False, max_length=30)  
    dob = models.DateTimeField(null=True)
    
    
class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    profile_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    caption = models.CharField(null=True, max_length=1000)
    profile_video = models.FileField(upload_to='user_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Challenges(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')
    challenge_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True)
    user_invitation = models.EmailField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    challenge_completed = models.BooleanField(default=False)
    