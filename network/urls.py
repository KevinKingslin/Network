
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("index/<str:following>", views.index, name="following"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createPost", views.createPost, name="createPost"),
    path("u/<int:user_id>", views.profile, name="profile"),

    #path("post/<str:request>/<int:id>", views.request, name="request")
    path("posts/edit/<int:post_id>", views.editPost, name="editPost"),
    path("posts/toggleLike/<int:post_id>", views.toggleLike, name="toggleLike"),
    path("posts/createcomment/<int:post_id>", views.CreateComment, name="CreateComment"),
    path("u/<int:user_id>/toggleFollow", views.toggleFollow, name="toggleFollow"),
    path("u/<int:user_id>/Mutual", views.MutualFollowers, name="Mutual"),
]