from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import random
from datetime import datetime

from network.serializers.serializer import LikeSerializer, UserSerializer
from .models import User, Post, UserFollowing, SearchHistory, Comment
from .recommend import Recommend

# View for main page
@login_required(login_url="login")
def index(request):
    # Initialise serializers
    serializer = UserSerializer()
    likeserializer = LikeSerializer()

    FromUser = User.objects.get(id=request.user.id)
    FollowingList = serializer.get_following(FromUser)

    # Get posts from users followed by the main user
    PostData = []
    if len(FollowingList) != 0:
        posts = list(
            Post.objects.filter(creator__in=FollowingList).order_by("-timestamp")
        )
        posts = random.sample(posts, len(posts))
    # If main user does not follow any user, return posts from any user
    else:
        items = list(Post.objects.all())
        posts = random.sample(items, 10)

    # Add like data and comment data for each post
    for post in posts:
        LikeUser = []
        likes = likeserializer.get_likes(post)
        for user in likes:
            LikeUser.append(User.objects.get(id=user))
        comments = Comment.objects.filter(post_id=post)
        PostData.append((post, LikeUser, comments.first(), comments.count()))

    # Initialise paginator class for pagination
    paginator = Paginator(PostData, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get a list of recommendations for the main user
    RecommendList = Recommend(FromUser)

    # Find number of mutual followers for each user recommendation
    MutualList = {}
    for user in RecommendList:
        MutualList[user] = MutualFollowerCount(FromUser, user)

    return render(
        request,
        "network/index.html",
        {
            "posts": page_obj,
            "postCount": len(posts),
            "RecommendList": RecommendList,
            "RecommendListCount": len(RecommendList),
            "MutualList": MutualList,
        },
    )


# Return number of mutual followers between 2 given users
def MutualFollowerCount(FromUser, user_id):
    Count = 0
    for record in FromUser.following.all():
        try:
            UserFollowing.objects.get(
                user_id=record.following_user_id, following_user_id=user_id
            )
            Count += 1
        except ObjectDoesNotExist:
            pass
    return Count


# View for profile page
@login_required(login_url="login")
def profile(request, user_id):
    if request.method == "GET":
        # Get the main user object
        fromUser = User.objects.get(id=request.user.id)

        # Get the user object the main user is visiting
        toUser = User.objects.get(id=user_id)

        # Initialise serializers
        serializer = UserSerializer()
        likeserializer = LikeSerializer()

        # Get followers and following of the touser
        following = serializer.get_following(toUser)
        followers = serializer.get_followers(toUser)

        # Add the touser to the main users' search history
        if fromUser.id != toUser.id:
            try:
                history = SearchHistory.objects.get(
                    user_id=fromUser, searched_user=toUser
                )
                history.created = datetime.now()
            except ObjectDoesNotExist:
                SearchHistory.objects.create(user_id=fromUser, searched_user=toUser)

        # Get whether the main user is already following the touser or not
        try:
            UserFollowing.objects.get(user_id=fromUser, following_user_id=toUser)
            following = True
        except ObjectDoesNotExist:
            following = False

        # Get number of mutual followers between main user and the touser
        mutualFollowerCount = MutualFollowerCount(fromUser, toUser)

        # Get all posts of touser order by new
        PostData = []
        posts = Post.objects.filter(creator=toUser).order_by("-timestamp")
        for post in posts:
            LikeUser = []
            likes = likeserializer.get_likes(post)
            for user in likes:
                LikeUser.append(User.objects.get(id=user))
            comments = Comment.objects.filter(post_id=post)
            PostData.append((post, LikeUser, comments.first(), comments.count()))

        return render(
            request,
            "network/profile.html",
            {
                "user": toUser,
                "posts": PostData,
                "following": following,
                "mutualFollowerCount": mutualFollowerCount,
            },
        )
    else:
        return HttpResponse("404")


# View for login page
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
            # Return error message
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


# View for logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


# View for register page
def register(request):
    if request.method == "POST":
        # Get form data
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
