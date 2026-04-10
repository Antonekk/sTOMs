from rest_framework import serializers

from .models import Therapist


class TherapistSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Therapist
        fields = ("id", "full_name", "office")
        read_only_fields = ("id", "full_name", "office")

    def get_full_name(self, obj):
        if not obj.therapist:
            return None
        return obj.therapist.get_full_name()
