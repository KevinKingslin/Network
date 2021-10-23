from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profilePicture = models.ImageField(upload_to='profilePictures/', null=True, blank=True)
    following = models.ForeignKey('self', related_name="followings", on_delete=models.CASCADE, blank=True, null=True)
    follower = models.ForeignKey('self', related_name="followers", on_delete=models.CASCADE, blank=True, null=True)
    likedBy = models.ManyToManyField('Post', related_name="likedBy", blank=True)

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    description = models.CharField(max_length=300)
    likes = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    edited = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add = True, editable=False)

    def __str__(self):
        return str(self.description)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add = True, editable=False)