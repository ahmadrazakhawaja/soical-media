from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follower = models.IntegerField(default=0)

class posts(models.Model):
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="User")
    content = models.TextField()
    likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class likes(models.Model):
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="User1")
    post = models.ForeignKey(posts,on_delete=models.CASCADE,related_name="post1")

class followers(models.Model):
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="User2")
    follower_id = models.IntegerField() 


