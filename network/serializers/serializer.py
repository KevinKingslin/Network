from django.contrib.auth import get_user_model
from network.models import Like, Post, UserFollowing, Comment, SearchHistory
from rest_framework import serializers

User = get_user_model()

# Serializer for user following data
class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ("id", "following_user_id", "created")

# Serializer for user followers data
class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ("id", "user_id", "created")

# Serializer for SearchHistory model
class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ("id", "searched_user_id", "created")

# Serializer for Comment model
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user_id","description", "post_id", "created")

# Serializer for Like model
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "user_id", "post_id")

    def get_likes(self, obj):
        return list(obj.post.values_list('user_id', flat=True))

# Serializer for User model
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

    # Returns list of users followed by main user
    def get_following(self, obj):
        return list(obj.following.values_list('following_user_id', flat=True))

    # Returns list of users following main user
    def get_followers(self, obj):
        return list(obj.followers.values_list('user_id', flat=True))

    # Returns list of search history records
    def get_history(self, obj):
        return list(obj.searchhistory.values_list('searched_user', flat=True))

    # Returns list of posts liked by the user
    def get_likes(self, obj):
        return list(obj.likedBy.values_list('post_id', flat=True))