from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class adding created_at/updated_at to any model that
    inherits it. Lives in `core/` (not `common/`) because — per our
    Milestone 0 rule of thumb — it IS meaningful outside this specific
    project (any Django app could use it), but here it's used as a
    foundational building block for SecureScan's own domain models
    (Profile, and later Scan, Report, etc.), which is what `core/` is for.

    `abstract = True` means Django does NOT create a database table for
    TimeStampedModel itself — it only contributes these two columns to
    whichever concrete model inherits it.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
