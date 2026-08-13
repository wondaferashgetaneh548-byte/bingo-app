from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class SMSLog(models.Model):
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.status}"