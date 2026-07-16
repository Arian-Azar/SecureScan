from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import LoginHistory, User
from .utils import get_client_ip, parse_client_user_agent


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles account creation. Two write-only password fields (not one) so
    the client confirms the password before it's ever sent to the server
    as a single value — catches typos client-side via `validate()` below,
    the same UX pattern as Django's own admin add-user form.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        # password_confirm never reaches User.objects.create_user() — it
        # exists only for this serializer's own validation, not as a model
        # field.
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Identical to SimpleJWT's own TokenObtainPairSerializer, except it also
    records a LoginHistory row on every successful login. This is the
    right layer to do it in (rather than a signal on user_logged_in,
    which JWT auth never fires, or the view) because `validate()` is the
    one place that both (a) has confirmed the credentials were correct and
    (b) has access to the request (via self.context) for IP/User-Agent.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')
        if request is not None:
            browser, device, os_family = parse_client_user_agent(request)
            LoginHistory.objects.create(
                user=self.user,
                ip_address=get_client_ip(request),
                browser=browser,
                device=device,
                os=os_family,
            )

        return data
