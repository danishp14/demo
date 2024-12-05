from django.urls import path
from .views import EmpRegisterView,EmployeeLoginView,EmployeeAPIView,EmployeeLogoutView,AboutUs,SocialLinks,ReviewAPI
from .views import CustomerRegisterView, CustomerLoginView,CustomerAPI,CarWashServiceView,ServicesCountAPIView, CustomerLogoutView 

urlpatterns = [

 path('empRegister/', EmpRegisterView.as_view(), name='empRegister'),
 path('employeeLogin/', EmployeeLoginView.as_view(), name='employeeLogin'),
 path('employeeLogout/', EmployeeLogoutView.as_view(), name='employeeLogout'),
 path('employeeAPI/', EmployeeAPIView.as_view(), name='employee'),
 path('employeeAPI/<int:pk>/', EmployeeAPIView.as_view(), name='employeeAPI'),

 path('customerRegister/', CustomerRegisterView.as_view(), name='customerRegister'),
 path('customerLogin/', CustomerLoginView.as_view(), name='customerLogin'),
 path('customerLogout/', CustomerLogoutView.as_view(), name='customerLogout'),
 path('customerAPI/',CustomerAPI.as_view(),name='customer'),
 path('customerAPI/<int:pk>/', CustomerAPI.as_view(), name='CustomerAPI'),


 path('carWashService/',CarWashServiceView.as_view(),name='carWashService'), 
 path('servicesCount/',ServicesCountAPIView.as_view(),name='servicesCount'),

 path('about_us/',AboutUs.as_view(),name='about_us'),
 path('social_links/',SocialLinks.as_view(),name='social_links'),

 path('review/',ReviewAPI.as_view(),name="review")
]
