from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from .managers import AppUserManager

from django.core.validators import RegexValidator


phone_validator = RegexValidator(r"^(?:\+48)?\d{9}$", "Invalid phone number")


class AppUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(_("phone number"), max_length=15, validators=[phone_validator], unique=True)
    first_name = models.CharField(_("first name"), max_length=64)
    last_name = models.CharField(_("last name"), max_length=64)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_token = models.CharField(max_length=36, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number, first_name, last_name"]

    objects = AppUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="patients")
    first_name = models.CharField(_("first name"), max_length=64)
    last_name = models.CharField(_("last name"), max_length=64)
    date_of_birth = models.DateField()
    
    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"