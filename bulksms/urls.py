from django.urls import path
from . import views

urlpatterns = [
    path('send-sms/', views.send_sms_view, name='send_sms'),
]