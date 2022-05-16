from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profilePicture = models.ImageField(upload_to='profilePictures/', null=True, blank=True)
    followerCount = models.IntegerField(default=0)
    followingCount = models.IntegerField(default=0)
    likedBy = models.ManyToManyField('Post', related_name="likedBy", blank=True)

class UserFollowing(models.Model):
    following = models.ForeignKey("User", related_name="following", on_delete=models.CASCADE)
    follower = models.ForeignKey("User", related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('following', 'follower',)

    def __str__(self):
        return str(f"{self.following} is following {self.follower}")

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