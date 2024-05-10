from django.urls import path
from . import views

app_name = 'apptevent'

urlpatterns = [

    # Appointment Routes
    path('apptevent/', views.CalendarView.as_view(), name='calendar'),
    path('apptevent/new/', views.event, name='event_new'),
    path('apptevent/edit/<int:event_id>/', views.event, name='event_edit'),
    path('apptevent/overview', views.appointment_overview, name='event_overview'),
    path('apptevent/doctor', views.AppointmentDoctor.as_view(), name='event_doctor'),

]
