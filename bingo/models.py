from django.db import models
from django.contrib.auth.models import User

# የደበደኛውን ቦርሳ ሂሳብ ለመያዝ
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.user.username} - {self.balance} ETB"

# የገንዘብ ማስገባት እና ማውጣት ታሪክ መዝገብ
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdrawal'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    payment_method = models.CharField(max_length=50, default='Telebirr')
    account_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='APPROVED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.amount} ETB ({self.status})"