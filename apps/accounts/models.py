from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom manager required whenever AUTH_USER_MODEL uses AbstractBaseUser
    instead of AbstractUser — Django has no built-in idea of how to create
    a user without a `username` field, so we tell it here.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user, authenticated by email instead of username.

    PermissionsMixin brings in is_superuser, groups, and user_permissions —
    required for the Django admin and for the Analyst/Admin roles described
    in the project proposal, without reimplementing that logic by hand.
    """

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    # `last_login` is already provided by AbstractBaseUser — no need to
    # redeclare it here.

    objects = UserManager()

    # Tells Django "authenticate with this field" instead of `username`.
    USERNAME_FIELD = 'email'
    # Fields prompted for by `createsuperuser`, IN ADDITION TO
    # USERNAME_FIELD and password (which are always required automatically).
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.email


class Profile(TimeStampedModel):
    """
    One-to-one extension of User for optional, non-authentication-related
    information. Kept separate from User itself (rather than adding these
    fields directly to User) for two reasons:
      1. Every write to these fields does not touch the auth-critical User
         row, keeping that table's write pattern simple and its history
         easy to reason about.
      2. It's the conventional Django pattern for "user metadata that grows
         over time" — new profile fields (later phases might add e.g. a
         subscription tier, or notification preferences) land here without
         ever touching User or its migrations.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    company = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    # IANA timezone name, e.g. "Europe/Berlin" — validated at the
    # serializer layer in Milestone 1.3, not here (models stay
    # presentation/validation-agnostic where practical).
    timezone = models.CharField(max_length=64, default='UTC')

    def __str__(self):
        return f'Profile<{self.user.email}>'


class LoginHistory(models.Model):
    """
    One row per successful login. Populated from CustomTokenObtainPairSerializer
    (see serializers.py) — NOT from a signal on User.last_login, because we
    also want the IP and parsed User-Agent, which only exist on the HTTP
    request itself, not on the User model.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-login_at']
        verbose_name_plural = 'login history'

    def __str__(self):
        return f'{self.user.email} @ {self.login_at:%Y-%m-%d %H:%M} from {self.ip_address}'
