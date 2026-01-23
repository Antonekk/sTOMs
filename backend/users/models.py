import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from offices.models import Office

from .managers import AppUserManager
from .validators import validate_only_letters, validate_patient_age

phone_validator = RegexValidator(r"^(?:\+48)?\d{9}$", _("Invalid phone number"))


class AppUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        CLIENT = "CLIENT", _("Klient")
        THERAPIST = "THERAPIST", _("Terapeuta")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("Adres email"), unique=True)
    phone_number = models.CharField(
        _("Numer telefonu"), max_length=15, validators=[phone_validator], unique=True
    )
    first_name = models.CharField(
        _("Imię"), validators=[validate_only_letters], max_length=64
    )
    last_name = models.CharField(
        _("Nazwisko"), validators=[validate_only_letters], max_length=64
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    role = models.CharField(
        _("Rola"),
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "first_name", "last_name"]

    objects = AppUserManager()

    class Meta:
        verbose_name = _("Użytkownik")
        verbose_name_plural = _("Użytkownicy")

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_therapist(self):
        return self.role == self.Role.THERAPIST

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        AppUser,
        verbose_name="Użytkownik",
        on_delete=models.PROTECT,
        related_name="patients",
        limit_choices_to={"role": AppUser.Role.CLIENT},
    )
    first_name = models.CharField(
        _("first name"), validators=[validate_only_letters], max_length=64
    )
    last_name = models.CharField(
        _("last name"), validators=[validate_only_letters], max_length=64
    )
    date_of_birth = models.DateField(
        _("Data urodzenia"), validators=[validate_patient_age]
    )

    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Pacjent główny"),
        help_text=_("Określa czy pacjent przypisany do klienta określa samego siebie"),
    )

    class Meta:
        verbose_name = _("Pacjent")
        verbose_name_plural = _("Pacjenci")
        ordering = ["-is_primary", "last_name", "first_name"]
        unique_together = ["user", "first_name", "last_name", "date_of_birth"]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Therapist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.OneToOneField(
        AppUser,
        verbose_name=_("Użytkownik"),
        on_delete=models.CASCADE,
        limit_choices_to={"role": AppUser.Role.THERAPIST},
        related_name="therapist",
        # TODO: Remove later
        null=True,
        blank=True,
    )
    office = models.OneToOneField(
        Office,
        on_delete=models.PROTECT,
        related_name="therapists",
        # TODO: Remove later
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Terapeuta")
        verbose_name_plural = _("Terapeuci")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
