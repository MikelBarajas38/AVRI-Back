"""
Database models.
"""

from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """
    Manager for custom user model.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        """
        if not email:
            raise ValueError('Email is required.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Create, save and return a new superuser.
        """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)

    EDUCATION_LEVELS = {
        'N': 'Sin estudios',
        'B': 'Bachillerato',
        'L': 'Licenciatura',
        'P': 'Posgrado',
    }

    education_level = models.CharField(
        max_length=255,
        choices=EDUCATION_LEVELS,
        default='N'
    )

    field_of_study = models.ForeignKey(
        'FieldOfStudy',
        on_delete=models.CASCADE,
        null=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Default field for authentication


class FieldOfStudy(models.Model):
    """
    Field of study model.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Document(models.Model):
    """
    Document model.
    """
    title = models.CharField(max_length=255)
    repository_uri = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    # updated_at = models.DateTimeField()

    DOCUMENT_STATUS = {
        'L': 'Acceso libre',
        'R': 'Restringido',
        'E': 'Embargado',
    }

    status = models.CharField(
        max_length=255,
        choices=DOCUMENT_STATUS,
        default='L'
    )

    def __str__(self):
        return self.title


class AuthoredDocument(models.Model):
    """
    Author and authored document relationship model.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} - {self.document}'


class SavedDocument(models.Model):
    """
    User and bookmarked document model.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.document}'


class ChatSession(models.Model):
    """
    Chat session model.
    """
    session_id = models.CharField(primary_key=True, max_length=255)
    session_name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    anonymous_session_id = models.UUIDField(
        default=None,
        null=True,
        blank=True
    )
    assistant_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f'{self.user.name} - {self.session_name}'
        return f'Anonymous session - {self.session_name}'

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, anonymous_session_id__isnull=True) |
                    models.Q(user__isnull=True, anonymous_session_id__isnull=False)
                ),
                name='user_xor_anonymous'
            )
        ]
