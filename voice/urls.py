"""HTTP URL patterns for voice module."""
from django.urls import path

from . import views

app_name = "voice"

urlpatterns = [
    path("incoming/", views.incoming_call, name="incoming"),
    path("status/", views.call_status, name="status"),
    path("agents/", views.agents_list, name="agents_list"),
]

