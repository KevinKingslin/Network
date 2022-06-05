
from django.urls import path

from . import views
from . import api_views

urlpatterns = [
    # View routes
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("u/<int:user_id>", views.profile, name="profile"),

    # API Routes

        # Post API routes
    path("createPost", api_views.createPost, name="createPost"),
    path("posts/edit/<int:post_id>", api_views.editPost, name="editPost"),
    path("posts/toggleLike/<int:post_id>", api_views.toggleLike, name="toggleLike"),
    path("posts/createcomment/<int:post_id>", api_views.CreateComment, name="CreateComment"),
    path("posts/likes/<int:post_id>", api_views.AllLikes, name="AllLikes"),
    path("posts/comments/<int:post_id>", api_views.AllComments, name="AllComments"),

        # User API routes
    path("u/<int:user_id>/toggleFollow", api_views.toggleFollow, name="toggleFollow"),
    path("u/<int:user_id>/Mutual", api_views.MutualFollowers, name="Mutual"),
    path("u/<int:user_id>/Followers", api_views.Followers, name="Followers"),
    path("u/<int:user_id>/Following", api_views.Following, name="Following"),
    path("searchuser/<str:query>", api_views.SearchUser, name="SearchUser"),
]