from django.db import models
from .Order import Order


class Call(models.Model):
    """Model to track ElevenLabs call history and conversations"""

    CALL_TYPE_CHOICES = [
        ('outbound', 'Outbound Phone Call'),
        ('inbound', 'Inbound Phone Call'),
        ('browser', 'Browser Voice Chat'),
    ]

    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calls',
        help_text='Associated order if this call is order-related'
    )
    phone_number = models.CharField(
        max_length=50,
        help_text='Customer phone number for outbound calls'
    )
    call_type = models.CharField(
        max_length=20,
        choices=CALL_TYPE_CHOICES,
        default='browser',
        help_text='Type of call (outbound, inbound, or browser)'
    )
    conversation_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Unique conversation ID from ElevenLabs'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='initiated',
        help_text='Current status of the call'
    )
    transcript = models.TextField(
        blank=True,
        null=True,
        help_text='Full conversation transcript'
    )
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text='Call duration in seconds'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context data for the call'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the call was initiated'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When the call record was last updated'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Call'
        verbose_name_plural = 'Calls'

    def __str__(self):
        return f"Call {self.conversation_id} - {self.call_type} ({self.status})"
