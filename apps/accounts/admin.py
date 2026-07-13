from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    """
    Shows Profile fields directly on the User's admin page instead of as a
    separate, disconnected admin section — since every User conceptually
    "has a" Profile, editing them together matches how an admin actually
    thinks about a user account.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Django's built-in UserAdmin assumes a `username` field throughout
    (fieldsets, ordering, search_fields, add_fieldsets) — since our User has
    no such field, every one of those must be redeclared here rather than
    just subclassing DjangoUserAdmin as-is.
    """

    inlines = [ProfileInline]

    ordering = ['email']
    list_display = ['email', 'full_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'full_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'avatar')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields shown on the "Add user" form specifically — deliberately
    # minimal (email + password twice, for confirmation), matching how
    # Django's own admin add-user form behaves.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
