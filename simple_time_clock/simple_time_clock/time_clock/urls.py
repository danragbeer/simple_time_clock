from django.urls import path

from . import views

urlpatterns = [
    path('', views.time_clock, name='time_clock'),
    path('shift_actions/', views.shift_actions, name="shift_actions"),
]