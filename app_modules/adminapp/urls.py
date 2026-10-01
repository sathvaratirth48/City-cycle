from django.contrib import admin
from django.urls import path,include
from app_modules.adminapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analytics/', views.analytics, name='analytics'),
    path('contact/list/', views.contact, name='list_contact'),
    
    #Login  
    path('register/', views.register_view, name='admin_register'),
    path('login/', views.login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('auth-reset-creative/', views.auth_reset_creative, name='auth-reset-creative'),
    path('auth-resetting-creative/', views.auth_resetting_creative, name='auth-resetting-creative'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),

    #city    
    path('create_City/', views.create_City, name='create_City'),
    path('list_city/', views.list_city, name='list_city'),
    path('delete_city/<int:id>/', views.delete_city, name='delete_city'),
    path('update_City/<int:id>/', views.update_City, name='update_City'),

    #vehicle Type  
    path('create_Vehicletype/', views.create_Vehicletype, name='create_Vehicletype'),
    path('list_vehicletype/', views.list_vehicletype, name='list_vehicletype'),
    path('delete_vehicletype/<int:id>/', views.delete_vehicletype, name='delete_vehicletype'),
    path('update_Vehicletype/<int:id>/', views.update_Vehicletype, name='update_Vehicletype'),
    
    #Category
    path('create_Category/', views.create_Category, name='create_Category'),
    path('list_category/', views.list_category, name='list_category'),
    path('delete_category/<int:id>/', views.delete_category, name='delete_category'),
    path('update_Category/<int:id>/', views.update_Category, name='update_Category'),
    
    # Vehicle
    path('create_Vehicle/', views.create_Vehicle, name='create_Vehicle'),
    path('list_vehicle/', views.list_vehicle, name='list_vehicle'),
    path('delete_vehicle/<int:id>/', views.delete_vehicle, name='delete_vehicle'),
    path('update_Vehicle/<int:id>/', views.update_Vehicle, name='update_Vehicle'),

    # Rental Location 
    path('create_RentalLocation/', views.create_RentalLocation, name='create_RentalLocation'),
    path('list_rentallocation/', views.list_rentallocation, name='list_rentallocation'),
    path('delete_rentallocation/<int:id>/', views.delete_rentallocation, name='delete_rentallocation'),
    path('update_RentalLocation/<int:id>/', views.update_RentalLocation, name='update_RentalLocation'),
    
    #Booking 
    path('list_booking/', views.list_Booking, name='admin_list_booking'),
    path('accept-booking/<int:id>/', views.accept_booking, name='accept_booking'),
    path('booking/reject/<int:id>/', views.reject_booking, name='reject_booking'),
    path('list_feedback/', views.list_feedback, name='admin_list_feedback'),
]