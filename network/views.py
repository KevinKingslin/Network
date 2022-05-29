from os import stat
from pydoc import cli
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.forms import fields
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.core.paginator import Paginator
from itertools import chain
import json
import random
from datetime import date, datetime

from network.serializers.serializer import LikeSerializer, UserSerializer, CommentSerializer
from .models import User, Post, UserFollowing, SearchHistory, Like, Comment
from .recommend import GetMutualFollowers, Recommend

class NewPostForm(forms.Form):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'newPostFormImage'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'newPostFormDesc', 'placeholder': "Hey, What's on your mind today?"}), required=True)

@login_required(login_url="login")
def index(request, following=None):
    serializer = UserSerializer()

    likeserializer = LikeSerializer()
    FromUser = User.objects.get(id=request.user.id)
    FollowingList = serializer.get_following(FromUser)

    PostData = []
    posts = list(Post.objects.filter(creator__in=FollowingList).order_by('-timestamp'))
    for post in posts:
        LikeUser = []
        likes = likeserializer.get_likes(post)
        for user in likes:
            LikeUser.append(User.objects.get(id=user))
        comments = Comment.objects.filter(post_id=post)
        PostData.append((post, LikeUser, comments.first(), comments.count()))
    
    paginator = Paginator(PostData, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    RecommendList = Recommend(FromUser)
    MutualList = {}
    for user in RecommendList:
        MutualList[user] = MutualFollowerCount(FromUser, user)

    return render(request, "network/index.html", {
        "newpostform": NewPostForm(),
        "posts": page_obj,
        "postCount": len(posts),
        "RecommendList": RecommendList,
        "RecommendListCount": len(RecommendList),
        "MutualList": MutualList,
    })

def Followers(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        serializer = UserSerializer()
        data = serializer.get_followers(ToUser)
        data = [User.objects.get(id=user) for user in data]
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)

def Following(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        serializer = UserSerializer()
        data = serializer.get_following(ToUser)
        data = [User.objects.get(id=user) for user in data]
        print(data)
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)

def MutualFollowers(request, user_id):
    if request.method == "GET":
        FromUser = User.objects.get(id=request.user.id)
        ToUser = User.objects.get(id=user_id)
        mutual = GetMutualFollowers(FromUser, ToUser)
        return JsonResponse([UserSerializer(user).data for user in mutual], safe=False)

def AllLikes(request, post_id):
    if request.method == "GET":
        serializer = LikeSerializer()
        post = Post.objects.get(id=post_id)
        data = serializer.get_likes(post)
        likes = [User.objects.get(id=user) for user in data]
        return JsonResponse([UserSerializer(user).data for user in likes], safe=False)

def AllComments(request, post_id):
    if request.method == "GET":
        data = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer
        comments = []
        for comment in data:
            CommentDetails = serializer(comment).data
            CommentDetails['profilePicture'] = comment.user_id.profilePicture.url
            CommentDetails['username'] = comment.user_id.username
            comments.append(CommentDetails)
        return JsonResponse(comments, safe=False)

@csrf_exempt
@login_required(login_url="login")
def createPost(request):
    if request.method == "POST":
        print(request.FILES)
        print(request.POST)
        creator = request.user
        post = Post.objects.create(creator=creator, description=request.POST.get('description'), image=request.FILES['image'])
        post.save()
        return HttpResponse(status=200)

@csrf_exempt
def CreateComment(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(user_id=request.user, post_id=post, description=data.get('comment'))
        comment.save()
        return HttpResponse(status=200)


@csrf_exempt
def editPost(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        post.description = data.get('new_desc')
        post.save()
        return HttpResponse(status=202)
    else:
        return HttpResponseRedirect(reverse("index"))


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


#Attributes for ranking:
#Mutual Followers
#Search history
#Influence of a user
#Number of posts - idk
#Number of likes - idk
#page rank - idk
#Common likes on a post

def MutualFollowerCount(FromUser, user_id):
    Count = 0
    for record in FromUser.following.all():
        try:
            UserFollowing.objects.get(user_id=record.following_user_id, following_user_id=user_id)
            Count += 1
        except ObjectDoesNotExist:
            pass
    return Count

def profile(request, user_id):
    if request.method == "GET":
        likeList = []
        fromUser = User.objects.get(id=request.user.id)
        toUser = User.objects.get(id=user_id)
        
        serializer = UserSerializer()
        likeserializer = LikeSerializer()
        following = serializer.get_following(toUser)
        followers = serializer.get_followers(toUser)

        if fromUser.id != toUser.id:
            try:
                history = SearchHistory.objects.get(user_id=fromUser, searched_user=toUser)
                history.created = datetime.now()
            except ObjectDoesNotExist:
                SearchHistory.objects.create(user_id=fromUser, searched_user=toUser)

        try:
            UserFollowing.objects.get(user_id=fromUser, following_user_id=toUser)
            following = True
        except ObjectDoesNotExist: 
            following = False

        mutualFollowerCount = MutualFollowerCount(fromUser, toUser)
        
        PostData = []
        posts = Post.objects.filter(creator = toUser).order_by('-timestamp')
        for post in posts:
            LikeUser = []
            likes = likeserializer.get_likes(post)
            for user in likes:
                LikeUser.append(User.objects.get(id=user))
            comments = Comment.objects.filter(post_id=post)
            PostData.append((post, LikeUser, comments.first(), comments.count()))

        for result in fromUser.likedBy.all():
            likeList.append(result.id)

        return render(request, "network/profile.html", {
            "user": toUser,
            "posts": PostData,
            "likes": likeList,
            "following": following,
            "mutualFollowerCount": mutualFollowerCount
        })
    else:
        return HttpResponse('404')

def SearchUser(request, query):
    if request.method == "GET":
        data = User.objects.filter(username__contains=query)[0:4]
        return JsonResponse([UserSerializer(user).data for user in data], safe=False)

@csrf_exempt
def toggleFollow(request, user_id):
    if request.method == "PUT":
        if(request.user.id == user_id):
            return HttpResponse(status=400)
        else:
            data = json.loads(request.body)
            fromUser = User.objects.get(id=request.user.id)
            toUser = User.objects.get(id=user_id)
            if data.get('follow') == "false":
                UserFollowing.objects.create(user_id=fromUser, following_user_id=toUser)
                fromUser.followingCount += 1
                toUser.followerCount += 1
                fromUser.save()
                toUser.save()
                return HttpResponse(status=200)
            elif data.get('follow') == "true":
                record = UserFollowing.objects.get(user_id=fromUser, following_user_id=toUser)
                record.delete()
                fromUser.followingCount -= 1
                toUser.followerCount -= 1
                fromUser.save()
                toUser.save()
                return HttpResponse(status=200)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
