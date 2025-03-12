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
