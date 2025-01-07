import random
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.db import models
import requests
from bs4 import BeautifulSoup
from ..lib.color_list import color_list


class CustomUserManager(BaseUserManager):
    """Personnalisation de la gestion des utilisateurs afin d'intégrer la gestion de l'authentification par token"""

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        username = self.generate_unique_username()
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and return a superuser with an email, password, and admin privileges.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

    def generate_unique_username(self):
        color_names = color_list
        for name in color_names:
            if not CustomUser.objects.filter(username=name).exists():
                return name
        raise ValueError("No unique usernames available.")


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Appliquer la gestion particulière de l'utilisateur au model customisé, qui hérite du model de django."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username