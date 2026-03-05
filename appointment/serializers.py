from rest_framework import serializers
from .models import Schedule, Appointment

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"