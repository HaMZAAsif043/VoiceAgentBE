from django.db import models

class Schedule(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
        
    day_of_week   = models.IntegerField(choices=DAYS)       
    start_time    = models.TimeField()                       
    end_time      = models.TimeField()                       
    slot_duration = models.IntegerField(default=30)         
    is_active     = models.BooleanField(default=True)

    class Meta:
        unique_together = ('day_of_week', 'start_time')

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"

class Appointment(models.Model):

    STATUS = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    google_event_id   = models.CharField(max_length=255, blank=True, null=True)
    meet_link         = models.URLField(blank=True, null=True)
    calendar_link     = models.URLField(blank=True, null=True)
    name         = models.CharField(max_length=100)
    phone        = models.CharField(max_length=20)
    email        = models.EmailField(blank=True)
    date         = models.DateField()                        # actual date
    start_time   = models.TimeField()                        # booked slot start
    end_time     = models.TimeField()                        # booked slot end
    status       = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'start_time')             # prevent double booking

    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time}"