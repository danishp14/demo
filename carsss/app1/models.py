from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from datetime import timedelta

# Admin & employee
class AdminEmployees(BaseUserManager):  # UserManeger
    def create_user(self, employee_name, salary  ,is_admin, password=None, password2=None):
        """ Creates and saves a User with the given email, dname,tc and password."""
        if not employee_name:
            raise ValueError("Employee must have an name")
        user = self.model(
            employee_name=employee_name,
            salary=salary,
            is_admin=is_admin,
        )
        user.set_password(password)
        user.save(using = self._db)

        return user
    
    def create_superuser(self, employee_name, salary  ,is_admin, password=None): 
        """Creates and saves a superuser with the given email, name,tc and password."""
        user = self.create_user(
            password=password,
            employee_name=employee_name,
            is_admin=is_admin,
            )
        user.is_admin = True
        user.save(using=self._db)
        return user

class EmployeesModel(AbstractBaseUser):
    employee_name = models.CharField(max_length=50,unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField(auto_now_add=True)
    last_working_day = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.employee_name} "
    
    objects = AdminEmployees()
    USERNAME_FIELD = "employee_name"
    REQUIRED_FIELDS = ["is_admin","salary"]

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True  # Admins have full permissions

    def has_module_perms(self, app_label):
        if self.is_admin:
            return True  # Admins can access all modules

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
    
# Customer
class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    employee = models.ForeignKey(EmployeesModel, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='customers')

    def __str__(self):
        return self.email
    
# Service records    
class CarWashService(models.Model):

    SERVICE_TYPE_CHOICES = [
    ("full_carwash", "Full Carwash - 70 Rupees"),
    ("inside_vacuum", "Inside Vacuum - 40 Rupees"),
    ("only_body", "Only Body - 30 Rupees"),
    ("full_with_polish", "Full with Polish - 100 Rupees"),
    ("only_polish", "Only Polish - 30 Rupees"),
    ]
# Defining prices for each service type
    SERVICE_PRICE = {
    "full_carwash": 70,
    "inside_vacuum": 40,
    "only_body": 30,
    "full_with_polish": 100,
    "only_polish": 30,
    }
    # Model fields
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default="full_carwash")
    service_date = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(EmployeesModel, null=True, blank=True, on_delete=models.CASCADE, 
                                 related_name="CarWashService")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    status = models.CharField(max_length=15, 
                              choices=[
                                    ("pending", "Pending"),
                                    ("completed", "Complete"),
                                    ("in_progress", "In Progress"),
                                  ], 
                                  default="pending")


    def __str__(self):
        return f"{self.SERVICE_TYPE_CHOICES()} on {self.service_date.strftime('%Y-%m-%d %H:%M:%S')}"


    @property
    def price(self):
        """Returns the price based on the selected service type."""
        return self.SERVICE_PRICE.get(self.service_type, 0)  # Default to 0 if no match
    
    
    # Making a static method in service for sales count
    @staticmethod
    def count_services_by_period(period):
        """Count services based on the period selected by the user."""
        today = timezone.now().date()
        # Filter by the user's period selection
        if period == "today":  #C ount of current day
            count = CarWashService.objects.filter(service_date__date=today).count()
        elif period == "yesterday":  #C ount of previous day
            yesterday = today - timedelta(days=1)
            count = CarWashService.objects.filter(service_date__date=yesterday).count()
        elif period == "weekly":  #C ount of weekly sales
            # Get the start of the current week (Monday) and end of the current week (Sunday)
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            end_of_week = start_of_week + timedelta(days=6)  # Sunday
            count = CarWashService.objects.filter(service_date__gte=start_of_week, service_date__lte=end_of_week).count()
        elif period == "this_month":  # Count of monthly sales
            count = CarWashService.objects.filter(service_date__month=today.month, service_date__year=today.year).count()
        else:
            count = 0 
        return count
