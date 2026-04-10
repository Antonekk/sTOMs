from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Patient


@receiver(pre_save, sender=Patient)
def patient_capitalize_first_name_and_last_name(sender, instance, **kwargs):
    if instance.first_name:
        instance.first_name = instance.first_name.capitalize()
    if instance.last_name:
        instance.last_name = instance.last_name.capitalize()
