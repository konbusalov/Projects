from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    full_name = models.CharField(max_length=20)
    passport = models.CharField(max_length=20)
    passport_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Changed from default 'user_set'
        related_query_name='user',
    )   
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed from default 'user_set'
        related_query_name='user',
    )

    def __str__(self):
        return self.username


class Bank(models.Model):
    name = models.CharField(max_length=100)
    bic = models.CharField(max_length=20)

class Enterprise(models.Model):
    name = models.CharField(max_length=100)
    unp = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='active')

class Loan(models.Model):
    MONTH_CHOICES = [
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
        (24, '24 месяца'),
        (36, '36 месяцев'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.IntegerField(choices=MONTH_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def total_amount(self, amount, interest_rate, months):
        return self.amount * (1 + self.interest_rate) ** self.months

    @property
    def total_interest(self):
        return self.total_amount - self.amount
        
class Lease(models.Model):
    MONTH_CHOICES = [
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
        (24, '24 месяца'),
        (36, '36 месяцев'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.IntegerField(choices=MONTH_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    @property
    def monthly_payment(self):
        return (self.amount * (1 + self.interest_rate/100)) / self.months

class Transfer(models.Model):
    from_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers'
    )
    to_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='incoming_transfers'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    
