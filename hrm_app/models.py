from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from datetime import time, timedelta
from django.utils import timezone
from decimal import Decimal

class Profile(models.Model):
    USERGROUP_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    name = models.CharField(max_length=100)
    usergroup = models.CharField(max_length=100, choices=USERGROUP_CHOICES)

    class Meta:  
        db_table = 'dashboard_profile'  

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('CL', 'Casual Leave'),       
        ('ML', 'Medical Leave'),
        ('EL', 'Emergency Leave'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES)

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    reason = models.TextField(blank=True, null=True)

    medical_proof = models.FileField(
        upload_to='medical_proofs/',
        blank=True,
        null=True
    )

    is_compensated = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    applied_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    days = models.PositiveIntegerField(blank=True, null=True)

    def clean(self):
        
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date.")

        if self.leave_type == 'ML' and not self.medical_proof:
            raise ValidationError("Medical proof is required for Medical Leave.")

        if (
            self.leave_type == 'EL'
            and self.status == 'Approved'
            and not self.is_compensated
        ):
            raise ValidationError(
                "Emergency Leave must be compensated before approval."
            )

    def save(self, *args, **kwargs):
        self.full_clean()  

        if self.start_date and self.end_date:
            self.days = (self.end_date - self.start_date).days + 1
        else:
            self.days = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} - {self.status}"


    
class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Module(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)
    icon_class = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
class Child(models.Model):
    module = models.ForeignKey(Module, related_name='children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Child of {self.module.name})"

class SubChild(models.Model):
    child = models.ForeignKey(Child, related_name='sub_children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (SubChild of {self.child.name})"

class SubSubChild(models.Model):
    subchild = models.ForeignKey(SubChild, related_name='subsubchildren', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (SubSubChild of {self.subchild.name})"
    


class Permission(models.Model):
    usergroup = models.ForeignKey(UserGroup, on_delete=models.CASCADE, null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    enabled = models.BooleanField(default=False)

class Department(models.Model):
    name = models.CharField(max_length=100)
    num_employees = models.IntegerField(default=0)  # Add this line
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    open_positions = models.PositiveIntegerField(default=0, help_text="Open job slots")


    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee'
    )

    full_name = models.CharField(max_length=100)
    
    date_of_birth = models.DateField(null=True, blank=True)  # ← Make optional
    
    blood_group = models.CharField(
        max_length=8,  # ← Increase to allow "AB+", "O-", etc.
        blank=True,    # ← Make optional
        help_text="Example: A+, B-, O-, AB+"
    )
    
    joining_date = models.DateField()
    
    designation = models.CharField(max_length=100, blank=True)  # ← Allow empty
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    email = models.EmailField(unique=True)
    
    phone = models.CharField(
        max_length=20,
        blank=True,  # ← Make optional
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid phone number.")]
    )

    emergency_number = models.CharField(
        max_length=20,
        blank=True,  # ← Make optional
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid emergency number.")]
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal('0.00')  # ← Good to have default
    )

    def __str__(self):
        return self.full_name
    

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

 

# attendance


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),   # ✅ ADD THIS
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    clock_in_datetime = models.DateTimeField(null=True, blank=True)
    clock_out_datetime = models.DateTimeField(null=True, blank=True)
    hours_worked = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Absent", choices=STATUS_CHOICES)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', 'user__username']

    def calculate_hours(self):
        """Calculate total hours worked based on clock in/out times"""
        if self.clock_in_datetime and self.clock_out_datetime:
            self.hours_worked = self.clock_out_datetime - self.clock_in_datetime
        else:
            self.hours_worked = None
        return self.hours_worked

    def determine_status(self):
        """Determine attendance status based on clock in/out times"""
        if not self.clock_in:
            return "Absent"

        # Office rules
        office_start = time(9, 0)       # 09:00 AM
        late_threshold = time(9, 15)    # Late after 9:15 AM
        minimum_hours = timedelta(hours=8)
        half_day_hours = timedelta(hours=4)

        if self.clock_in and self.clock_out:
            self.calculate_hours()
            if self.clock_in <= late_threshold and self.hours_worked >= minimum_hours:
                return "Present"
            elif self.clock_in > late_threshold and self.hours_worked >= minimum_hours:
                return "Late"
            elif self.hours_worked >= half_day_hours:
                return "Half Day"
            else:
                return "Absent"
        else:
            # Only clock-in available yet
            if self.clock_in <= late_threshold:
                return "Present"
            else:
                return "Late"

    def save(self, *args, **kwargs):
        self.calculate_hours()
    # ✅ Don't overwrite On Leave status
        if self.status != 'On Leave':
          self.status = self.determine_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"

    @property
    def is_present(self):
        """Check if employee is currently clocked in but not clocked out"""
        return self.clock_in and not self.clock_out

    @property
    def formatted_hours(self):
        """Readable HH:MM format for total worked time"""
        if self.hours_worked:
            total_seconds = int(self.hours_worked.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}"
        return "--:--"
    
    
    
    
# holiday


class Holiday(models.Model):
    HOLIDAY_TYPE_CHOICES = [
        ('common', 'Common Leave'),
        ('company', 'Company Leave'),
    ]

    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"
        

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.notification.title}"
    

class Payroll(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='payrolls')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.CharField(max_length=20)
    year = models.IntegerField(default=timezone.now().year)  
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def net_salary(self):
        return (self.basic_salary + self.hra + self.bonus) - self.deductions

    def __str__(self):
        return f"{self.employee.full_name} - {self.month} {self.year}"
