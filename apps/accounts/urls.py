from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # TokenObtainPairView/TokenRefreshView are used directly (not
    # wrapped) — they already do exactly what "login" and "refresh" need,
    # and SimpleJWT reads USERNAME_FIELD from AUTH_USER_MODEL dynamically,
    # so this form (email + password) just works with our custom User.
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
