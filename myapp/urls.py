from django.urls import path
from .views import add_and_list_students

urlpatterns = [
    path('students/', add_and_list_students, name='students'),
]