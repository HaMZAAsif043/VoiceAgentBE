from rest_framework import serializers
from datetime import datetime, timedelta
from .models import Schedule, Appointment

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        appointment_date = data.get('date')

        # Auto-compute end_time if missing or same as start_time
        if start_time and (not end_time or end_time <= start_time):
            # Try to derive slot duration from the schedule for that day
            slot_minutes = 30  # default fallback
            if appointment_date:
                day_of_week = appointment_date.weekday()
                schedule = Schedule.objects.filter(
                    day_of_week=day_of_week, is_active=True
                ).first()
                if schedule:
                    slot_minutes = schedule.slot_duration

            start_dt = datetime.combine(appointment_date or datetime.today().date(), start_time)
            end_dt = start_dt + timedelta(minutes=slot_minutes)
            data['end_time'] = end_dt.time()

        # Final guard: end_time must be after start_time
        if data.get('end_time') and data.get('start_time') and data['end_time'] <= data['start_time']:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })

        return data