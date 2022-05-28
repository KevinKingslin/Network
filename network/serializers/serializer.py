from django.contrib.auth import get_user_model
from network.models import Like, Post, UserFollowing, Comment, SearchHistory
from rest_framework import serializers

User = get_user_model()

class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ("id", "following_user_id", "created")

class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ("id", "user_id", "created")

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ("id", "searched_user_id", "created")

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user_id","description", "post_id", "created")

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "user_id", "post_id")

    def get_likes(self, obj):
        return list(obj.post.values_list('user_id', flat=True))

class UserSerializer(serializers.ModelSerializer):

    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "following",
            "followers",
            "profilePicture"
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_following(self, obj):
        return list(obj.following.values_list('following_user_id', flat=True))

    def get_followers(self, obj):
        return list(obj.followers.values_list('user_id', flat=True))

    def get_history(self, obj):
        return list(obj.searchhistory.values_list('searched_user', flat=True))

    def get_likes(self, obj):
        return list(obj.likedBy.values_list('post_id', flat=True))