from django.contrib.auth import get_user_model
from network.models import UserFollowing
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
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_following(self, obj):
        return FollowingSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj):
        return FollowersSerializer(obj.followers.all(), many=True).data