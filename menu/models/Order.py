from django.db import models


class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=50)
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)

    items = models.JSONField()  # store ordered items list
    total_price = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
