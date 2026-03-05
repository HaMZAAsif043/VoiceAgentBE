# analytics/urls.py
from django.urls import path
from appointment.views import (
    AvailableSlotsView,
    AppointmentCreateView,
    AppointmentCancelView,
    AppointmentListView,
    schedule
)

urlpatterns = [
    path('schedule/', schedule, name='schedule'),
    path('slots/', AvailableSlotsView.as_view(), name='slots'),
    path('create/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('cancel/<int:pk>/', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('all/', AppointmentListView.as_view(), name='appointment-list'),
]

