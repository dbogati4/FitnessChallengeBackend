from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("getusers", views.get_users, name="get_users"),
    path("signup", views.user_signup, name="user_signup"),
    path("login", views.user_login, name="user_login"),
    path("otp", views.otp_verification, name="otp_verification"),
    path("onboarding", views.user_onboard, name="user_onboard"),
    path("home", views.home, name="home"),
    path("createchallenges", views.post_challenges, name="post_challenges"),
    path("viewchallenges", views.get_chanellenges, name="get_chanellenges"),
    path("uploadposts", views.create_post, name="create_post"),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]