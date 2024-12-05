from rest_framework import serializers
from .models import EmployeesModel,Customer,CarWashService,Reviewmodel
from django.contrib.auth.hashers import make_password
import re

# Admin and Employee
class EmployeeSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type":"password"},write_only=True)
    class Meta:
        model = EmployeesModel
        fields = ["id", "employee_name", "salary","is_admin","password","password2"]

    # Validating empname
    def validate_employee_name(self, value):  # Using validation on empNAME
        if EmployeesModel.objects.filter(employee_name=value).exists() :
            raise serializers.ValidationError("Employee with this name is already there ") 
        if not value[0].isalpha():
            raise serializers.ValidationError("Employee name must start with a letter.")
        if not re.match(r'^[A-Za-z][A-Za-z0-9@]*$', value):
            raise serializers.ValidationError("Employee name can only contain letters, numbers, and the '@' symbol.") 
        number_part = ''.join([ch for ch in value if ch.isdigit()])
        if number_part and int(number_part) > 999:
            raise serializers.ValidationError("Employee name number part should not exceed 999.")       
        return value
    
    # Check if password is equal passord2
    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        return data
    
    # Took password2 so need to do method create  
    def create(self,validate_data):
        return EmployeesModel.objects.create_user(**validate_data)

# Emp loginSerializer
class EmployeeLoginSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = EmployeesModel
        fields = ["employee_name","password"]

class EmpSee(serializers.ModelSerializer):
    class Meta:
        model = EmployeesModel
        fields = ["employee_name", "salary", "is_admin", "last_working_day"]


# Emp serializer for crud operation
class EmpManage(serializers.ModelSerializer):
    class Meta:
        model = EmployeesModel
        fields = ["employee_name", "salary", "is_admin", "password", "last_working_day", "is_active"]
    
# Customer
class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = Customer
        fields = ["email", "first_name", "last_name", "password", "password_confirm"]

    # Ensure passwords match
    def validate(self, data):
        
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        customer = Customer.objects.create(**validated_data)
        customer.password = make_password(password)  # set the hashed password
        customer.save()
        return customer

# Customer Login Serializer
class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# Customer serializer for crud operation
class CustomerSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields=["id", "email", "first_name", "last_name", "is_active"]


# Serializer for records of serives
class CarWashServiceSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=EmployeesModel.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    status = serializers.ChoiceField(choices=[
                                        ("pending", "Pending"), 
                                        ("completed", "Completed"), 
                                        ("in_progress", "In Progress"),
                                        ])
    class Meta:
        model = CarWashService
        fields = ["id", "service_type", "employee", "customer", "status", "final_price", "service_date"]

    # Check if the employee exists in the database
    def validate_employee(self, value):
        return value

    # Check if the customer exists in the database
    def validate_customer(self, value):
        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reviewmodel
        fields = ["ratings","review"]

    def validate_ratings(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Ratings must be between 1 and 5.")
        if not isinstance(value, int):
            raise serializers.ValidationError("Rating must be an integer.")
        return value
    
    def validate_review(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Review text cannot be empty.")
        return value
