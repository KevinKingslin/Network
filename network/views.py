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
from datetime import date, datetime
from .models import User, Post, UserFollowing, SearchHistory, Like
from .recommend import Recommend

class NewPostForm(forms.Form):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'newPostFormImage'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'newPostFormDesc', 'placeholder': "Hey, What's on your mind today?"}), required=True)

@login_required(login_url="login")
def index(request, following=None):
    likeList = []
    try:
        user = User.objects.get(id=request.user.id)
    except:
        return JsonResponse({"error": "Incorrect credentials."}, status=404)

    if following == None:
        posts = list(Post.objects.all().order_by('-timestamp'))
    # elif following == "following":
    #     posts = [Post.objects.filter(creator=users) for users in user.followings.all()]
    #     posts = list(chain(*posts))
    #     posts.sort(key=lambda x: x.timestamp, reverse=True)

    for result in user.likedBy.all():
        likeList.append(result.id)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "newpostform": NewPostForm(),
        "username": request.user.username,
        "posts": page_obj,
        "postCount": len(posts),
        "likes": likeList
    })


@login_required(login_url="login")
def createPost(request):
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            creator = request.user
            description = form.cleaned_data["description"]
            try:
                image = form.cleaned_data["image"]
            except:
                image = None
            post = Post(creator=creator, description=description, image=image)
            post.save()
            return HttpResponseRedirect(reverse("index"))
    elif request.method == "PUT":
        pass


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
                post.likedBy.add(user)
                post.likes += 1
            elif data["liked"] == "false":
                post.likedBy.remove(user)
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


def profile(request, user_id):
    if request.method == "GET":
        likeList = []
        fromUser = User.objects.get(id=request.user.id)
        toUser = User.objects.get(id=user_id)
        posts = Post.objects.filter(creator = toUser).order_by('-timestamp')
        followerCount = toUser.followerCount
        followingCount = toUser.followingCount

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

        Recommend(fromUser)

        mutualFollowerCount = 0
        for record in fromUser.following.all():
            try:
                UserFollowing.objects.get(user_id=record.following_user_id, following_user_id=toUser)
                mutualFollowerCount += 1
            except ObjectDoesNotExist:
                pass

        for result in fromUser.likedBy.all():
            likeList.append(result.id)

        return render(request, "network/profile.html", {
            "user": toUser,
            "posts": posts,
            "likes": likeList,
            "following": following,
            "followerCount": followerCount,
            "followingCount": followingCount,
            "mutualFollowerCount": mutualFollowerCount
        })
    else:
        return HttpResponse('404')


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
    return HttpResponseRedirect(reverse("index"))


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

        # Attempt to create new user
        # Test
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
