from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/

    Deliberately does NOT log the user in / return tokens on success —
    email verification (a later task in this same milestone) will sit
    between "account created" and "account usable", so returning tokens
    here would let an unverified account act as if it were verified.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


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
