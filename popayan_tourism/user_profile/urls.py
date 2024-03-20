from django.urls import path
from . import views

app_name = "user_profile"

urlpatterns = [
    # path("profile/", views.profile, name="profile"),
    # path("profile/update/", views.update_profile, name="update_profile"),
    # path('rtoken/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
