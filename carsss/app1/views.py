# Standard library imports
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect,HttpResponseRedirect

# Third-party imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken  # token
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

# Local imports
from .models import EmployeesModel, Customer, CarWashService,Reviewmodel
from .serializer import (
    EmployeeSerializer,EmployeeLoginSerializer,EmpManage,EmpSee,
    CustomerSerilizer,CustomerRegisterSerializer,CustomerLoginSerializer,
    CarWashServiceSerializer,ReviewSerializer,
)

User = get_user_model()
# For token (access and refresh)
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),      
    }


# Employeee and admin 
# Signup for employees
class EmpRegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register
    
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)  # Getting the data from user side
        if serializer.is_valid():  # Validating the data
            emp = serializer.save()  # Saving the validated data
            return Response(
                {"message":"success"},
                status=status.HTTP_201_CREATED
            ) 
        else:
            print(serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


# Login for employees
class EmployeeLoginView(APIView):
    permission_classes=[AllowAny]  # allow anyone  

    def post(self, request):
        serializer = EmployeeLoginSerializer(data=request.data)  # getting data from user    
        if serializer.is_valid():  # validated data
            employee_name = request.data.get("employee_name")  # tracting the employee name from the validated data
            password = request.data.get("password")  # tracting the password from the validated data
            # check if the username & password provided by the user exists or not  
            employee = authenticate(request, username=employee_name, password=password)
            if employee is not None:
                token = get_tokens_for_user(employee)
                return Response(
                        {
                            "token": token, 
                            "message": "success"
                        }, 
                        status=status.HTTP_200_OK)      
            else:
                return Response({
                            "error": {"non_field_error": ["Email or password is not valid"]}    
                        }, 
                        status=status.HTTP_401_UNAUTHORIZED
                        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Logout for employees
class LogoutView(APIView):
    permission_classes = [AllowAny]  # Ensure the user is authenticated to log out

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail":"Successfully logged out."}, 
                status=status.HTTP_200_OK,
                )
        except TokenError:
            return Response(
                {"error":"Invalid token or token is expired."}, 
                status=status.HTTP_400_BAD_REQUEST,
                )


# Crud for emp if admin is true 
class EmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        if request.user.is_admin:  # Check if the current user is admin
            emp = EmployeesModel.objects.all()
            serilizer=EmpSee(emp,many=True)
            return Response(serilizer.data)  # Returning data from(db) serialized data to user
        return Response(
                    {"detail": "Permission denied.(You are not admin)"},  # If user is not admin this will be printed
                    status=status.HTTP_403_FORBIDDEN
                    )

    def post(self, request):
        if request.user.is_admin:
            serializer = EmployeeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
                {"detail": "Permission denied.(You are not admin)"}, 
                status=status.HTTP_403_FORBIDDEN
                )
    
    def put(self,request,pk):
        if request.user.is_admin:
            employee = get_object_or_404(EmployeesModel,pk=pk)
            Serializer = EmpManage(employee,data=request.data,)  # if partial add partial=True after request.data
            if Serializer.is_valid():
                Serializer.save()
                return Response(Serializer.data,status=status.HTTP_200_OK)
            return Response(Serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(
                    {"detail": "Permission denied.(You are not admin)"}, 
                    status=status.HTTP_403_FORBIDDEN
                    )

    def delete(self, request, pk):
        if request.user.is_admin:
            try:
                employee = EmployeesModel.objects.get(pk=pk)
                employee.delete()
                return Response(
                    {"detail": "Employee deleted."}, 
                    status=status.HTTP_204_NO_CONTENT
                    )
            except EmployeesModel.DoesNotExist:
                return Response(
                    {"detail": "Employee not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                    )
        return Response(
            {"detail": "Permission denied.(You are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )

# Customer
# Signup for customer
class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                "message": "Customer registered successfully!",
                "customer": {
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login for customer
class CustomerLoginView(APIView):
    permission_classes = [AllowAny]
   
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            
            try:
                customer = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response(
                    {"detail": "Customer not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Check the password for the customer
            if not check_password(password, customer.password):
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                if customer.employee_id is None:
                # Dynamically fetch the first admin employee
                    default_employee = EmployeesModel.objects.filter(is_admin=True).first()
        
                    if not default_employee:
                        return Response(
                            {"detail": "No admin employee available to assign."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
                    token = get_tokens_for_user(default_employee)
                else:
                        # Use the assigned employee
                    employee = customer.emp_id
                    token = get_tokens_for_user(employee)
                # Generate JWT tokens for the customer
                return Response(
                    {   
                        "access": token["access"],  # Access token
                        "refresh": token["refresh"],  # Refresh token
                    },
                    status=status.HTTP_200_OK
                    )
            except EmployeesModel.DoesNotExist:
                return Response(
                    {"detail": "Employee not found for this customer."}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Crud operation for Customer 
class CustomerAPI(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated
   
    def get(self, request):
        if request.user.is_admin:
            try:
                customer = Customer.objects.filter(Q(employee=request.user) | Q(employee__isnull=True))
                serializer = CustomerSerilizer(customer,many=True)         
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Customer.DoesNotExist:
                return Response(
                    {"detail": "Customer not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                    )
        return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )
        
    def post(self, request):
        # Check if the current user is admin
        if request.user.is_admin:
            serializer = CustomerRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )

    def put(self,request,pk):
        if request.user.is_admin:
            customer = get_object_or_404(Customer,pk=pk)
            serializer = CustomerRegisterSerializer(customer,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )
    
    def delete(self, request, pk):
        if request.user.is_admin:
            try:
                customer = Customer.objects.get(pk=pk)
                customer.delete()
                return Response(
                    {"detail": "customer deleted."}, 
                    status=status.HTTP_204_NO_CONTENT
                    )
            except EmployeesModel.DoesNotExist:
                return Response(
                    {"detail": "customer not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                    )
        return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )

# Services
# Making services record here
class CarWashServiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        if request.user.is_admin:    
            empid = request.user.id
            empid = request.query_params.get("empid", None)
            if empid :
                services = CarWashService.objects.filter(employee__employee_name=empid)
                serializer=CarWashServiceSerializer(services,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                services = CarWashService.objects.all()
            serializer = CarWashServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Permission denied.(You are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )

    def post(self, request):
        if not request.user.is_admin:
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CarWashServiceSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data["customer"]
            # Calculate applicable discount
            discount = customer.discount_remaining  # Use existing discount if available
            if discount == 0:
                # Count completed services for this customer
                completed_services = CarWashService.objects.filter(
                    customer=customer, status="completed"
                ).count()
                # Calculate how many free services they should have received
                free_service_threshold = 50  # Every 50 services grants 1 free service
                free_services_earned = completed_services // free_service_threshold
                # Check if customer is eligible for a new free service
                if free_services_earned > customer.free_services_used:
                    discount = 100  # Free service
                    customer.free_services_used = free_services_earned  # Update the free services count
                    customer.discount_remaining = discount
                    customer.save()
                elif completed_services >= 45:
                    discount = 30  # 30% discount
                elif completed_services >= 35:
                    discount = 20  # 20% discount
                elif completed_services >= 5:
                    discount = 5  # 5% discount

            # Validate the service type
            service_type = serializer.validated_data["service_type"]
            if service_type not in CarWashService.SERVICE_PRICE:
                return Response(
                    {"detail": "Invalid service type."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the base price for the selected service type
            base_price = CarWashService.SERVICE_PRICE.get(service_type, 0)
            # Apply the discount
            if discount == 100:
                discounted_price = 0
            else:
                discounted_price = base_price - (base_price * discount / 100)
            # Save the service entry after applying discount
            service = serializer.save()
            service.final_price = discounted_price
            service = serializer.save()


            # Reset discount after use (if applicable)
            customer.discount_remaining = 0
            customer.save()

            # Response data to be sent back
            response_data = {
                "message": "Car wash service created successfully!",
                "id": service.id,
                "base_price": base_price,
                "discount": f"{discount}% applied" if discount > 0 else "No discount applied",
                "final_price": discounted_price,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Sales count
class ServicesCountAPIView(APIView):
    permission_classes=[IsAuthenticated]  # Ensure that the user is authenticated

    def post(self, request):
        if request.user.is_admin:    
            period = request.data.get("period", "today")  #Weekly Sale
            try:
                services = CarWashService.count_services_by_period(period) 
                count_today = services.count()

                total_earnings = sum(service.final_price  if service.final_price is not None else 0 for service in services)
                serializer=CarWashServiceSerializer(services,many=True)
            except ValueError as e:
                raise ValidationError(str(e))   # Will return a 400 error with the message
            # Return the count and period in the response
            response_data = {
                'count': count_today,
                "total_earnings":total_earnings,
                'services': serializer.data,
            }

            return Response(response_data)
        return Response(
            {"detail": "Permission denied.(You are not admin)"},
              status=status.HTTP_403_FORBIDDEN
              )
    
# About_Us
class AboutUs(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request):
        return HttpResponse("Carsss is a leading car wash company dedicated to providing top-notch vehicle cleaning services. With a focus on quality, convenience, and customer satisfaction, \n we have \n Full Carwash: \n Inside Vacuum: \n Only Body: \n Full with Polish: \n Only Polish: ")

# Sociallinks
class SocialLinks(APIView):
    permission_classes = [AllowAny]
    PLATFORM_REDIRECTS = {
            "facebook": "https://www.facebook.com/login.php/",
            "youtube": "https://www.youtube.com/",
            "instagram": "https://www.instagram.com/accounts/login/",
            "twitter": "https://www.twitter.com/login",
        }
    
    def post(self, request):
        platform_name = request.data.get("name")
        redirect_url = self.PLATFORM_REDIRECTS.get(platform_name)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return Response(
                {"error": "Platform not supported"}, 
                status=status.HTTP_400_BAD_REQUEST
                )

class ReviewPagination(PageNumberPagination):
    page_size = 2 # Number of reviews per page
    page_size_query_param = 'page_size'  # Allow the client to specify page size
    max_page_size = 3  # Limit the maximum page size


class ReviewAPI(APIView):
    permission_classes= [IsAuthenticated]
            
    def post(self,request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review= serializer.save()
            return Response(
                        {"message": "review and rating created successfully!", 
                         "review": review.review,
                         "ratings":review.ratings},
                        status=status.HTTP_201_CREATED
                        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GiveReviews(APIView):
    permission_classes= [AllowAny]

    def get(self, request):     
        reviews = Reviewmodel.objects.all()
        paginator = ReviewPagination()  # Create an instance of the custom pagination class
        paginated_reviews = paginator.paginate_queryset(reviews, request)  # Apply pagination to the queryset
	    # Serialize the paginated data
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)  # Return paginated response
    