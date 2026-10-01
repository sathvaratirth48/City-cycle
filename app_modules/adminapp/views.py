from django.shortcuts import render,redirect
from app_modules.adminapp import forms
from app_modules.adminapp import models
from app_modules.adminapp.models import Vehicle
from app_modules.userapp.models import CustomUser

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from app_modules.userapp.models import Booking, Feedback
from django.db.models import Count, Sum
from app_modules.adminapp.models import Vehicle, City
from app_modules.adminapp.models import Vehicle_type
from app_modules.adminapp.models import Vehicle, Vehicle_type
from django.utils import timezone
from rest_framework import viewsets
from .models import City
from .serializers import CitySerializer
import json

from datetime import date

# Create your views here. 

# ================= INDEX / DASHBOARD =================
def index(request):
    User = get_user_model()

    active_bookings = Booking.objects.filter(
        booking_status__in=['Confirmed', 'Ongoing']
    )
    for booking in active_bookings:
        booking.auto_update_status()

    # Fresh counts — update ke baad
    total_bookings     = Booking.objects.count()
    pending_bookings   = Booking.objects.filter(booking_status='Pending').count()
    confirmed_bookings = Booking.objects.filter(booking_status='Confirmed').count()
    completed_bookings = Booking.objects.filter(booking_status='Completed').count() 
    cancelled_bookings = Booking.objects.filter(booking_status='Cancelled').count()
    ongoing_bookings   = Booking.objects.filter(booking_status='Ongoing').count()

    total_revenue = Booking.objects.filter(
        payment_status='Paid'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    paid_count   = Booking.objects.filter(payment_status='Paid').count()
    unpaid_count = Booking.objects.filter(payment_status='Unpaid').count()

    total_users    = User.objects.filter(role__in=['Parent', 'User']).count()
    approved_users = User.objects.filter(is_approved=True, role__in=['Parent', 'User']).count()

    total_vehicles = Vehicle.objects.count()
    total_cities   = City.objects.count()

    # Monthly chart data
    today = date.today()
    monthly_labels, monthly_bookings_data, monthly_revenue_data = [], [], []
    for i in range(11, -1, -1):
        month = today.month - i
        year  = today.year
        while month <= 0:
            month += 12
            year  -= 1
        from datetime import date as d
        month_date = d(year, month, 1)
        monthly_labels.append(month_date.strftime('%b/%y'))
        cnt = Booking.objects.filter(
            booking_date__year=year,
            booking_date__month=month
        ).count()
        rev = Booking.objects.filter(
            booking_date__year=year,
            booking_date__month=month,
            payment_status='Paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_bookings_data.append(cnt)
        monthly_revenue_data.append(int(rev))

    recent_bookings = Booking.objects.select_related(
        'user', 'vehicle'
    ).order_by('-id')[:6]

    vt = list(
        Vehicle_type.objects.annotate(
            count=Count('vehicle')
        ).values('type_name', 'count')
    )

    context = {
        'total_bookings':     total_bookings,
        'pending_bookings':   pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings, 
        'cancelled_bookings': cancelled_bookings,
        'ongoing_bookings':   ongoing_bookings,
        'total_revenue':      total_revenue,
        'paid_count':         paid_count,
        'unpaid_count':       unpaid_count,
        'total_users':        total_users,
        'approved_users':     approved_users,
        'total_vehicles':     total_vehicles,
        'total_cities':       total_cities,
        'recent_bookings':    recent_bookings,
        'monthly_labels':         json.dumps(monthly_labels),
        'monthly_bookings_data':  json.dumps(monthly_bookings_data),
        'monthly_revenue_data':   json.dumps(monthly_revenue_data),
        'vt_labels': json.dumps([v['type_name'] for v in vt]),
        'vt_data':   json.dumps([v['count'] for v in vt]),
    }
    
    return redirect('analytics')


# ================= ANALYTICS =================
def analytics(request):

    active_bookings = Booking.objects.filter(
        booking_status__in=['Confirmed', 'Ongoing']
    )
    for booking in active_bookings:
        booking.auto_update_status()

    # Fresh counts
    total_bookings     = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(booking_status='Confirmed').count()
    completed_bookings = Booking.objects.filter(booking_status='Completed').count() 
    cancelled_bookings = Booking.objects.filter(booking_status='Cancelled').count()
    pending_bookings   = Booking.objects.filter(booking_status='Pending').count()
    ongoing_bookings   = Booking.objects.filter(booking_status='Ongoing').count()

    total_revenue = Booking.objects.filter(
        payment_status='Paid'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    paid_bookings   = Booking.objects.filter(payment_status='Paid').count()
    unpaid_bookings = Booking.objects.filter(payment_status='Unpaid').count()

    # Monthly data
    today = date.today()
    monthly_labels = []
    monthly_data   = []
    monthly_revenue = []

    for i in range(11, -1, -1):
        month = today.month - i
        year  = today.year
        while month <= 0:
            month += 12
            year  -= 1
        month_date = date(year, month, 1)
        monthly_labels.append(month_date.strftime('%b/%y'))
        count = Booking.objects.filter(
            booking_date__year=year,
            booking_date__month=month
        ).count()
        revenue = Booking.objects.filter(
            booking_date__year=year,
            booking_date__month=month,
            payment_status='Paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_data.append(count)
        monthly_revenue.append(int(revenue))

    User = get_user_model()
    total_users    = User.objects.filter(role__in=['Parent', 'User']).count()
    approved_users = User.objects.filter(
        is_approved=True, role__in=['Parent', 'User']
    ).count()

    total_vehicles = Vehicle.objects.count()
    vehicle_types  = list(
        Vehicle_type.objects.annotate(
            count=Count('vehicle')
        ).values('type_name', 'count')
    )

    recent_bookings = Booking.objects.select_related(
        'user', 'vehicle'
    ).order_by('-id')[:5]

    context = {
        'total_bookings':     total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,  
        'cancelled_bookings': cancelled_bookings,
        'pending_bookings':   pending_bookings,
        'ongoing_bookings':   ongoing_bookings,
        'total_revenue':      total_revenue,
        'paid_bookings':      paid_bookings,
        'unpaid_bookings':    unpaid_bookings,
        'total_users':        total_users,
        'approved_users':     approved_users,
        'total_vehicles':     total_vehicles,
        'monthly_labels':     json.dumps(monthly_labels),
        'monthly_data':       json.dumps(monthly_data),
        'monthly_revenue':    json.dumps(monthly_revenue),
        'vt_labels': json.dumps([v['type_name'] for v in vehicle_types]),
        'vt_data':   json.dumps([v['count'] for v in vehicle_types]),
        'recent_bookings':    recent_bookings,
    }
    return render(request, 'adminapp/analytics.html', context)

#Contact US  
def contact(request):
    contac = models.Contact.objects.all()
    context = {'contac':contac}
    return render(request,'adminapp/list_Contact.html',context)

#Login Start

def auth_reset_creative(request):
    return render(request, 'adminapp/auth-reset-creative.html')

def auth_resetting_creative(request):
    return render(request, 'adminapp/auth-resetting-creative.html')



#Login Strart
User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        role = request.POST.get('role')

        # Only admin can register
        if role != 'Admin':
            messages.error(request, "Only Admin registration is allowed here!")
            return redirect('admin_register')

        if password != password1:
            messages.error(request, "Passwords do not match!")
            return redirect('admin_register')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists!")
            return redirect('admin_register')

        user = User.objects.create_user(
            username=username,
            password=password,
            role='Admin' 
        )
        user.is_approved = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        messages.success(request, "Admin registered successfully!")
        return redirect('admin_login')

    return render(request, 'adminapp/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ admin can login in admindashboard
            if user.role != 'Admin':
                messages.error(request, "Access denied! Only Admins can login here.")
                return redirect('admin_login')

            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('admin_dashboard')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'adminapp/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('admin_login')


@login_required
def admin_dashboard(request):
    if request.user.role != 'Admin':
        messages.error(request, "You are not authorized!")
        return redirect('admin_login')

    all_users = User.objects.exclude(role='Admin')
    approved_users = User.objects.filter(is_approved=True, role='User')
    pending_users = User.objects.filter(is_approved=False, role='User')

    return render(request, 'adminapp/dashboard_admin.html', {
        'all_users': all_users,
        'approved_users': approved_users,
        'rejected_users': pending_users,
    })


@login_required
def approve_user(request, user_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized!")
        return redirect('admin_login')

    user = get_object_or_404(User, id=user_id)

    if user.role == 'Admin':
        messages.warning(request, "Cannot approve Admin!")
        return redirect('admin_dashboard')

    user.is_approved = True
    user.save()
    messages.success(request, f"{user.username} approved!")
    return redirect('admin_dashboard')


@login_required
def reject_user(request, user_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized!")
        return redirect('admin_login')

    user = get_object_or_404(User, id=user_id)

    if user.role == 'Admin':
        messages.warning(request, "Cannot reject Admin!")
        return redirect('admin_dashboard')

    user.is_approved = False
    user.save()
    messages.error(request, f"{user.username} rejected!")
    return redirect('admin_dashboard')


def parent_dashboard(request):
    return render(request, 'adminapp/dashboard_parent.html')

def user_dashboard(request):
    return render(request, 'adminapp/dashboard_user.html')

#Login End 

#City Start 
def create_City(request):
    if request.method == 'POST':
        form = forms.city_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(list_city)
        else:
            print(form.errors)
    return render(request, 'adminapp/create_City.html') 

def list_city(request):
    city = models.City.objects.all()
    context = {'city':city}
    return render(request, 'adminapp/list_city.html',context) 

def delete_city(request,id):
    cit1 = models.City.objects.get(id=id)
    cit1.delete()
    return redirect(list_city)

def update_City(request,id):
    cit2 = models.City.objects.get(id=id)
    if request.method == 'POST':
        form = forms.city_form(request.POST, request.FILES, instance=cit2)
        if form.is_valid():
            form.save()
            return redirect(list_city)
        else:
            print(form.errors)
    context = {'cit2': cit2}
    return render(request,'adminapp/update_City.html',context)

#City End   

#City REST API
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('-id')
    serializer_class = CitySerializer


#vehicle Type Start
def create_Vehicletype(request):
    if request.method == 'POST':
        form = forms.vehicletype_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(list_vehicletype)
        else:
            print(form.errors)
    return render(request, 'adminapp/create_Vehicletype.html') 

def list_vehicletype(request):
    vehitype = models.Vehicle_type.objects.all()
    context = {'vehitype':vehitype}
    return render(request, 'adminapp/list_vehicletype.html',context) 

def delete_vehicletype(request,id):
    vehicletype1 = models.Vehicle_type.objects.get(id=id)
    vehicletype1.delete()
    return redirect(list_vehicletype)

def update_Vehicletype(request,id):
    vehicletype2 = models.Vehicle_type.objects.get(id=id)
    if request.method == 'POST':
        form = forms.vehicletype_form(request.POST, request.FILES, instance=vehicletype2)
        if form.is_valid():
            form.save()
            return redirect(list_vehicletype)
        else:
            print(form.errors)
    context = {'vehicletype2': vehicletype2}
    return render(request,'adminapp/update_Vehicletype.html',context)

#vehicle Type End 


#Category Start
def create_Category(request):
    vtype = models.Vehicle_type.objects.all() 
    if request.method == 'POST':
        form = forms.category_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(list_category)
        else:
            print(form.errors)
    context = {'vtype': vtype} 
    return render(request, 'adminapp/create_Category.html', context)

def list_category(request):
    category = models.Category.objects.all()
    context = {'category':category}
    return render(request, 'adminapp/list_category.html',context)

def delete_category(request,id):
    cate = models.Category.objects.get(id=id)
    cate.delete()
    return redirect(list_category)

def update_Category(request,id):
    categ = models.Category.objects.get(id=id)
    vtype = models.Vehicle_type.objects.all()
    if request.method == 'POST':
        form = forms.category_form(request.POST, request.FILES, instance=categ)
        if form.is_valid():
            form.save()
            return redirect(list_category)
        else:
            print(form.errors)
    context = {'categ':categ, 'vtype': vtype}
    return render(request,'adminapp/update_Category.html',context)

#Category End 

#Vehicle Start    
def create_Vehicle(request):
    vtype = models.Vehicle_type.objects.all() 
    cat = models.Category.objects.all()         
    city = models.City.objects.all()
    vehicles = models.Vehicle.objects.all()        
    if request.method == 'POST':
        form = forms.vehicle_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(list_vehicle)
        else:
            print(form.errors)
    context = {'vtype': vtype, 'cat': cat, 'city': city, 'vehicles': vehicles}
    return render(request, 'adminapp/create_Vehicle.html', context)

def list_vehicle(request):
    vehicle = models.Vehicle.objects.all()
    context = {'vehicle': vehicle}
    return render(request, 'adminapp/list_vehicle.html', context)

def delete_vehicle(request,id):
    vehi = models.Vehicle.objects.get(id=id) 
    vehi.delete()
    return redirect(list_vehicle)

def update_Vehicle(request,id):
    vehi1 = models.Vehicle.objects.get(id=id)
    vtype = models.Vehicle_type.objects.all()
    cat = models.Category.objects.all()
    city = models.City.objects.all()
    if request.method == 'POST':
        form = forms.vehicle_form(request.POST, request.FILES, instance=vehi1)
        if form.is_valid():
            form.save()
            return redirect(list_vehicle)
        else:
            print(form.errors)
    context = {'vehi1': vehi1, 'vtype': vtype, 'cat': cat,'city': city}
    return render(request,'adminapp/update_Vehicle.html',context)

#Vehicle End     

# Rental Location Start 
def create_RentalLocation(request):
    city = models.City.objects.all() 
    if request.method == 'POST':
        form = forms.rentallocation_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(list_rentallocation)
        else:
            print(form.errors)
    context = {'city': city}
    return render(request, 'adminapp/create_RentalLocation.html', context)

def list_rentallocation(request):
    rentallocation = models.RentalLocation.objects.all()
    context = {'rentallocation': rentallocation}
    return render(request, 'adminapp/list_rentallocation.html', context)

def delete_rentallocation(request,id):
    rentallo = models.RentalLocation.objects.get(id=id)
    rentallo.delete()
    return redirect(list_rentallocation)

def update_RentalLocation(request,id):
    rentallo1 = models.RentalLocation.objects.get(id=id)
    city = models.City.objects.all() 
    if request.method == 'POST':
        form = forms.rentallocation_form(request.POST, request.FILES, instance=rentallo1)
        if form.is_valid():
            form.save()
            return redirect(list_rentallocation)
        else:
            print(form.errors)
    context = {'rentallo1': rentallo1, 'city': city}
    return render(request,'adminapp/update_RentalLocation.html',context)

# Rental Location End 

#List Bookings For Admin

def list_Booking(request):
    all_bookings = Booking.objects.all().order_by('-booking_date')
    for booking in all_bookings:
        booking.auto_update_status() 
    booking = Booking.objects.all().order_by('-booking_date')
    return render(request, 'adminapp/list_Booking.html', {'booking': booking})

# ── Accept  Booking ─────────────────────────────────────────────

def accept_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.booking_status = 'Confirmed'
    booking.confirmed_at = timezone.now()  #  Time store
    booking.save()
    messages.success(request, f"Booking #{id} confirmed!")
    return redirect('admin_list_booking')

# ── Reject  Booking ─────────────────────────────────────────────
def reject_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.booking_status = 'Cancelled'
    booking.save()
    return redirect('admin_list_booking')

@login_required
def list_feedback(request):
    if request.user.role != 'Admin':
        return redirect('login')

    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'adminapp/list_feedback.html', {'feedbacks': feedbacks})
