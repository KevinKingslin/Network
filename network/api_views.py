from .models import User, UserFollowing, Post, Comment, Like
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from network.serializers.serializer import (
    LikeSerializer,
    UserSerializer,
    CommentSerializer,
)

# API view to create new post
@csrf_exempt
def createPost(request):
    if request.method == "POST":
        creator = request.user
        post = Post.objects.create(
            creator=creator,
            description=request.POST.get("description"),
            image=request.FILES["image"],
        )
        post.save()
        return HttpResponse(status=200)


# API view to edit existing post
@csrf_exempt
def editPost(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        post.description = data.get("new_desc")
        post.save()
        return HttpResponse(status=202)
    else:
        return HttpResponseRedirect(reverse("index"))


# API view to add or delete likes to a post by the user
@csrf_exempt
@login_required(login_url="login")
def toggleLike(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(username=request.user.username)
        except:
            return JsonResponse({"error": "Incorrect post details"}, status=404)
        data = json.loads(request.body)
        if data.get("liked") is not None:
            if data["liked"] == "true":
                like = Like.objects.create(user_id=user, post_id=post)
                like.save()
                post.likes += 1
            elif data["liked"] == "false":
                like = Like.objects.get(user_id=user, post_id=post)
                like.delete()
                post.likes -= 1
            post.save()
            return HttpResponse(status=202)
        else:
            return HttpResponse(status=402)


# API view to create new comment to a post
@csrf_exempt
def CreateComment(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(
            user_id=request.user, post_id=post, description=data.get("comment")
        )
        comment.save()
        return HttpResponse(status=200)


# API view for the user to start following another user
@csrf_exempt
def toggleFollow(request, user_id):
    if request.method == "PUT":
        if request.user.id == user_id:
            return HttpResponse(status=400)
        else:
            data = json.loads(request.body)
            fromUser = User.objects.get(id=request.user.id)
            toUser = User.objects.get(id=user_id)
            if data.get("follow") == "false":
                UserFollowing.objects.create(user_id=fromUser, following_user_id=toUser)
                fromUser.followingCount += 1
                toUser.followerCount += 1
            elif data.get("follow") == "true":
                record = UserFollowing.objects.get(
                    user_id=fromUser, following_user_id=toUser
                )
                record.delete()
                fromUser.followingCount -= 1
                toUser.followerCount -= 1
            fromUser.save()
            toUser.save()
            return HttpResponse(status=200)


# Return list of mutual followers between 2 users
def MutualFollowers(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        mutual = GetMutualFollowers(FromUser, ToUser)
        return JsonResponse([UserSerializer(user).data for user in mutual], safe=False)


# Return all followers of a user
def Followers(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        serializer = UserSerializer()
        data = serializer.get_followers(ToUser)
        data = [User.objects.get(id=user) for user in data]
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)


# Return all following of a user
def Following(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        serializer = UserSerializer()
        data = serializer.get_following(ToUser)
        data = [User.objects.get(id=user) for user in data]
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)


# Return list of first order users and thier edges to the main user
def GetDegreeData(fromUser):
    # Intialise serializer
    serializer = UserSerializer()
    AllEdges = []

    # Get all following of the main user
    FirstOrderFollowing = serializer.get_following(fromUser)

    for user_id in FirstOrderFollowing:
        FollowUser = User.objects.get(id=user_id)
        AllEdges.append((fromUser.id, user_id))

        for SecondUser in serializer.get_following(FollowUser):

            # Add all edges between first order neighbours and second order neighbours
            if SecondUser != fromUser.id:
                AllEdges.append((FollowUser.id, SecondUser))

    return FirstOrderFollowing, AllEdges


# Return lsit of mutual followers between 2 users
def GetMutualFollowers(FromUser, ToUser):
    serializer = UserSerializer()
    FirstOrderFollowing, AllEdges = GetDegreeData(FromUser)
    SecondOrder = []

    # Get first order neighbours
    for user_id in FirstOrderFollowing:
        FollowUser = User.objects.get(id=user_id)

        # Get second order neighbours
        for seconduser in serializer.get_following(FollowUser):
            if seconduser == ToUser.id:
                SecondOrder.append(FollowUser)

    SecondOrder = list(set(SecondOrder))
    return SecondOrder


# Return all likes given on a post
def AllLikes(request, post_id):
    if request.method == "GET":
        serializer = LikeSerializer()
        post = Post.objects.get(id=post_id)
        data = serializer.get_likes(post)
        likes = [User.objects.get(id=user) for user in data]
        return JsonResponse([UserSerializer(user).data for user in likes], safe=False)


# Return all comments made on a post
def AllComments(request, post_id):
    if request.method == "GET":
        data = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer
        comments = []
        for comment in data:
            CommentDetails = serializer(comment).data
            CommentDetails["profilePicture"] = comment.user_id.profilePicture.url
            CommentDetails["username"] = comment.user_id.username
            comments.append(CommentDetails)
        return JsonResponse(comments, safe=False)


# Return search results to a search user query
def SearchUser(request, query):
    if request.method == "GET":
        data = User.objects.filter(username__contains=query)[0:4]
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)
