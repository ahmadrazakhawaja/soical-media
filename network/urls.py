
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("following/posts", views.following, name="following"),
    path("edit", views.edit, name="edit"),
    path("like", views.likesx, name="likes")
]
