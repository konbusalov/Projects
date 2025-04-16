from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from math import ceil

class Bank(models.Model):
    name = models.CharField(max_length=100)

class Enterprise(models.Model):
    name = models.CharField(max_length=100)
    unp = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('OPERATOR', 'Operator'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
        ('SPECIALIST', 'Specialist')
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')

    
    full_name = models.CharField(max_length=20)
    passport = models.CharField(max_length=20)
    passport_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    banks = models.ManyToManyField(Bank, through='Account', related_name='clients')
    enterprise = models.ForeignKey(
        Enterprise, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='specialists'
    )

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

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'role': 'CLIENT'})
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, null=True, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)


    account_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='active')

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4())[:20]  # First 20 chars of UUID
        super().save(*args, **kwargs)



class Loan(models.Model):
    MONTH_CHOICES = [
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
        (24, '24 месяца'),
        (36, '36 месяцев'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.IntegerField(choices=MONTH_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank=True, related_name='approved_loans')

    @property
    def total_amount(self):
        return self.amount * (1 + self.interest_rate) ** self.months

    @property
    def total_interest(self):
        return ceil(self.total_amount - self.amount)
    
    def approve(self, manager: User):
        if not manager.role == 'MANAGER':
            raise ValueError("Only managers can approve loans")
        self.status = 'APPROVED'
        self.approved_by = manager
        self.save()

    def reject(self, manager: User):
        if not manager.role == 'MANAGER':
            raise ValueError("Only managers can reject loans")
        self.status = 'REJECTED'
        self.approved_by = manager
        self.save()
        
class Lease(models.Model):
    MONTH_CHOICES = [
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
        (24, '24 месяца'),
        (36, '36 месяцев'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.IntegerField(choices=MONTH_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank=True, related_name='approved_leases')

    @property
    def monthly_payment(self):
        return ceil((self.amount * (1 + self.interest_rate/100)) / self.months)

    def approve(self, manager: User):
        if not manager.role == 'MANAGER':
            raise ValueError("Only managers can approve leases")
        self.status = 'APPROVED'
        self.approved_by = manager
        self.save()

    def reject(self, manager: User):
        if not manager.role == 'MANAGER':
            raise ValueError("Only managers can reject leases")
        self.status = 'REJECTED'
        self.approved_by = manager
        self.save()

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='from_account')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='to_account')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    




    
