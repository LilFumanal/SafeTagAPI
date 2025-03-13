import random
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
import logging
logger = logging.getLogger(__name__)
from django.db import models
from ..lib.color_list import color_list


class CustomUserManager(BaseUserManager):
    """Personnalisation de la gestion des utilisateurs afin d'intégrer la gestion de l'authentification par token"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        username = self.get_unique_username()
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser with an email, password, and admin privileges.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

    def get_unique_username(self):
        color_names = list(color_list)
        while color_names:
            # Select a random color name
            username = random.choice(color_names)
                
                # Check if the username already exists in the User table
            if not CustomUser.objects.filter(username=username).exists():
                return str(username)
                # If the username is taken, remove it from the list to avoid selecting it again
            color_names.remove(username)        
            # If no unique username is found (highly unlikely), return a fallback name
        return "UniqueColorUser"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Appliquer la gestion particulière de l'utilisateur au model customisé, qui hérite du model de django."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # Add related_name to avoid clashes
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Add related_name to avoid clashes
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username}-{self.email}"