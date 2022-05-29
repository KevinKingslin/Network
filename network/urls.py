
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("index/<str:following>", views.index, name="following"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("u/<int:user_id>", views.profile, name="profile"),

    #path("post/<str:request>/<int:id>", views.request, name="request")
    path("createPost", views.createPost, name="createPost"),
    path("posts/edit/<int:post_id>", views.editPost, name="editPost"),
    path("posts/toggleLike/<int:post_id>", views.toggleLike, name="toggleLike"),
    path("posts/createcomment/<int:post_id>", views.CreateComment, name="CreateComment"),
    path("u/<int:user_id>/toggleFollow", views.toggleFollow, name="toggleFollow"),
    path("u/<int:user_id>/Mutual", views.MutualFollowers, name="Mutual"),
    path("u/<int:user_id>/Followers", views.Followers, name="Followers"),
    path("u/<int:user_id>/Following", views.Following, name="Following"),
    path("posts/likes/<int:post_id>", views.AllLikes, name="AllLikes"),
    path("posts/comments/<int:post_id>", views.AllComments, name="AllComments"),
    path("searchuser/<str:query>", views.SearchUser, name="SearchUser"),
]