from django.db import models
from django.contrib.auth.models import User

class Resident(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unit_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    move_in_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Unit {self.unit_number}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('rent', 'Rent'),
        ('additional', 'Additional Services'),
        ('maintenance', 'Maintenance'),
        ('debt', 'Debt'),
    ]
    
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.resident.unit_number} - {self.payment_type} - Ksh.{self.amount}"

class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.resident.unit_number} - {self.title}"

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('delayed', 'Delayed'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('normal', 'Normal'),
    ]
    
    order_id = models.CharField(max_length=10, unique=True)
    unit_number = models.CharField(max_length=10)
    category = models.CharField(max_length=50)
    assigned_to = models.CharField(max_length=100)
    days_late = models.IntegerField(default=0)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order_id} - Unit {self.unit_number}"

class Unit(models.Model):
    UNIT_STATUS = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
        ('upcoming', 'Upcoming'),
    ]
    
    unit_number = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=20, choices=UNIT_STATUS)
    image = models.ImageField(upload_to='units/', null=True, blank=True)
    
    def __str__(self):
        return f"Unit {self.unit_number}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title