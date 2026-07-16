from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from .utils import generate_email_verification_token, read_email_verification_token


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/

    The created account starts INACTIVE (is_active=False) and stays that
    way until /verify-email/ is called with a valid token — Django's
    authenticate() rejects inactive users automatically, so login is
    blocked for free, with no extra check needed in the login view.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False
        user.save(update_fields=['is_active'])
        self._send_verification_email(user)

    def _send_verification_email(self, user):
        token = generate_email_verification_token(user)
        # NOTE: there's no frontend yet, so the "link" is really just the
        # raw token, meant to be POSTed to /api/auth/verify-email/ by
        # whatever client (Swagger, a future frontend, curl) is testing
        # this. Once a frontend exists, this becomes a real URL like
        # f'{FRONTEND_URL}/verify-email?token={token}'.
        send_mail(
            subject='Verify your SecureScan account',
            message=(
                f'Hi {user.full_name},\n\n'
                f'Use this token to verify your account:\n\n{token}\n\n'
                f'This token expires in 24 hours.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class VerifyEmailView(APIView):
    """POST /api/auth/verify-email/   body: {"token": "<token>"}"""

    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response(
                {'detail': 'token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = read_email_verification_token(token)
        if user_id is None:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response({'detail': 'Email already verified.'})

        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'detail': 'Email verified successfully.'})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Swaps in CustomTokenObtainPairSerializer so every successful login is
    recorded as a LoginHistory row (see serializers.py for why that logic
    lives in the serializer's validate(), not here).
    """
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    POST /api/auth/logout/   body: {"refresh": "<refresh_token>"}

    JWT access tokens can't be individually revoked before they expire —
    that's inherent to how stateless JWTs work. What we CAN do is
    blacklist the refresh token, so even though the current access token
    stays valid until it naturally expires (at most ACCESS_TOKEN_LIFETIME
    minutes, per base.py), the client can never mint a new one after this
    call. Requiring IsAuthenticated means only the token's own owner can
    invalidate it.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid or already-blacklisted refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)
