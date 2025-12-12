from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Resident(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('moved_out', 'Moved Out'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unit_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    move_in_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Unit {self.unit_number}"
    
    def get_payment_status(self):
        """Check if tenant has paid current month"""
        from datetime import date
        current_month = date.today().month
        payment = Payment.objects.filter(
            resident=self,
            due_date__month=current_month,
            paid=True
        ).first()
        return 'paid' if payment else 'pending'

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('rent', 'Rent'),
        ('additional', 'Additional Services'),
        ('maintenance', 'Maintenance'),
        ('debt', 'Debt'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]
    
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='payments')
    month = models.CharField(max_length=20, default='')  # e.g., "December 2025"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='rent')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    transaction_code = models.CharField(max_length=100, blank=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.resident.unit_number} - {self.payment_type} - Ksh.{self.amount}"
    
    @property
    def balance(self):
        return self.amount - self.amount_paid
    
    def save(self, *args, **kwargs):
        # Auto-update status
        if self.amount_paid >= self.amount:
            self.status = 'paid'
            self.paid = True
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif date.today() > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'pending'
        super().save(*args, **kwargs)

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
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hvac', 'HVAC'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('landscaping', 'Landscaping'),
        ('painting', 'Painting'),
        ('carpentry', 'Carpentry'),
        ('pest_control', 'Pest Control'),
        ('general', 'General Maintenance'),
    ]
    
    order_id = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200, default='')
    description = models.TextField(default='')
    unit_number = models.CharField(max_length=10)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey('Subcontractor', on_delete=models.SET_NULL, null=True, blank=True, related_name='work_orders')
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    days_late = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.title if self.title else self.category}"
    
    @property
    def contractor_name(self):
        return self.assigned_to.name if self.assigned_to else 'Unassigned'

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

class ParkingSlot(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('available', 'Available'),
    ]
    
    slot_number = models.CharField(max_length=10, unique=True)  # e.g., P-101A
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='parking_slots')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['slot_number']
    
    def __str__(self):
        return f"{self.slot_number} - {self.status}"
    
    @property
    def unit_number(self):
        """Get unit number from resident"""
        return self.resident.unit_number if self.resident else ''
    
    @property
    def tenant_name(self):
        """Get tenant name from resident"""
        return self.resident.user.get_full_name() if self.resident else ''
    
class Subcontractor(models.Model):
    CATEGORY_CHOICES = [
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('hvac', 'HVAC Technician'),
        ('cleaner', 'Cleaning Services'),
        ('security', 'Security'),
        ('landscaper', 'Landscaping'),
        ('painter', 'Painter'),
        ('carpenter', 'Carpenter'),
        ('pest_control', 'Pest Control'),
        ('general', 'General Maintenance'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 0.00 to 5.00
    joined_date = models.DateField(default=date.today)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"
    
    def active_work_orders_count(self):
     """Count active work orders assigned to this contractor"""
     return WorkOrder.objects.filter(
        assigned_to=self,
        status__in=['new', 'open', 'in_progress']
    ).count()

class Unit(models.Model):
    UNIT_STATUS = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    UNIT_TYPE_CHOICES = [
        ('studio', 'Studio'),
        ('1br', '1 Bedroom'),
        ('2br', '2 Bedrooms'),
        ('3br', '3 Bedrooms'),
        ('4br', '4 Bedrooms'),
    ]
    
    unit_number = models.CharField(max_length=10, unique=True)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='1br')
    floor = models.IntegerField(default=1)
    size_sqm = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Size in square meters")
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=UNIT_STATUS, default='vacant')
    resident = models.OneToOneField(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_unit')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='units/', null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    resident = models.ForeignKey('Resident', on_delete=models.SET_NULL, null=True, blank=True, related_name='unit')
    class Meta:
        ordering = ['unit_number']
    
    def __str__(self):
        return f"Unit {self.unit_number}"
    
    @property
    def tenant_name(self):
        if self.resident:
            return self.resident.user.get_full_name()
        return 'Vacant'
    
    @property
    def tenant_phone(self):
        if self.resident:
            return self.resident.phone
        return '-'