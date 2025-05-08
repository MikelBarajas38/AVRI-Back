"""
Database models.
"""

import uuid

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

    def create_user(
            self,
            email=None,
            password=None,
            is_anonymous=False,
            **extra_fields
    ):
        """
        Create, save and return a new user.
        """

        if is_anonymous:
            extra_fields.setdefault('is_anonymous', True)
            extra_fields.setdefault('anonymous_id', uuid.uuid4())
            user = self.model(**extra_fields)
            user.set_unusable_password()
        else:
            if not email:
                raise ValueError(
                    'The Email field must be set for non-anonymous users'
                )
            user = self.model(
                email=self.normalize_email(email),
                **extra_fields
            )
            if password:
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
    email = models.EmailField(max_length=255, unique=True, null=True)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)

    is_anonymous = models.BooleanField(default=False)
    anonymous_id = models.UUIDField(
        default=None,
        null=True,
        blank=True,
        unique=True
    )

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

    def __str__(self):
        if self.is_anonymous:
            return f'Anonymous User {self.anonymous_id}'
        return self.email


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
    id = models.CharField(primary_key=True, max_length=255)
    title = models.CharField(max_length=255)
    repository_uri = models.URLField()
    repository_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    assistant_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.session_name}'


class SatisfactionSurveyResponse(models.Model):
    """
    Model to store flexible satisfaction survey responses as JSON.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='survey_responses'
    )
    version = models.CharField(max_length=255)
    survey = models.JSONField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.completed_at.strftime('%Y-%m-%d')}'


class UserProfile(models.Model):
    """
    User profile model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} profile - {self.created_at.strftime('%Y-%m-%d')}'
