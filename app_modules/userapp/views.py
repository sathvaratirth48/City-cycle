import random
import os
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from django.shortcuts import render,redirect
from django.utils.timezone import now

from app_modules.adminapp.models import RentalLocation,Vehicle

from app_modules.userapp import forms
from app_modules.adminapp.models import Vehicle
from app_modules.userapp import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import ProfileForm, RegisterForm
from app_modules.adminapp import models as admin_models
from .forms import RegisterForm
# Create your views here.     

def home_page(request):
    vehicles  = Vehicle.objects.all()[:6]
    locations = RentalLocation.objects.all()
    ecycles   = Vehicle.objects.all()
    context   = {
        'vehicles' : vehicles,
        'locations': locations,
        'ecycles'  : ecycles,
    }
    return render(request, 'userapp/index.html', context)

#Search   
def search_results(request):
    if request.method == 'POST':
        print("POST DATA:", request.POST)
        pickup_location_id = request.POST.get('pickup_location')
        drop_location_id = request.POST.get('drop_location')
        pickup_date = request.POST.get('pickup_date')
        pickup_time = request.POST.get('pickup_time')
        ecycle_id = request.POST.get('ecycle')
        print("Date:", pickup_date, "Time:", pickup_time)

        results = Vehicle.objects.filter(id=ecycle_id)
        for v in results:
            print("Image:", v.vehicle_img)
        context = {
            'results'        : results,
            'pickup_location': RentalLocation.objects.get(id=pickup_location_id),
            'drop_location'  : RentalLocation.objects.get(id=drop_location_id),
            'pickup_date'    : pickup_date,
            'pickup_time'    : pickup_time,
        }
        return render(request, 'userapp/search_results.html', context)
    return redirect('home_page')


def about_page(request):
    return render(request,'userapp/about.html')

#Booking Start  

# ── Booking ──────────────────────────────────────────────────────────────────
@login_required
def booking_page(request, id):
    vehicle = Vehicle.objects.get(id=id)
    rental_locations = admin_models.RentalLocation.objects.all()

    if request.method == 'POST':
        form = forms.BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.vehicle = vehicle
            booking.user = request.user
            booking.booking_status = "Pending"
            booking.total_hours = int(float(form.cleaned_data.get('total_hours') or 0))
            booking.save()
            messages.success(request, "Booking created successfully!")
            return redirect('list_Booking_user')
        else:
            messages.error(request, "Please fix the errors below.")
            print(form.errors) 
    else:
        form = forms.BookingForm()

    return render(request, 'userapp/booking.html', {
        'form': form,
        'vehicle': vehicle,
        'rental_locations': rental_locations,
    })

# ── List Bookings ───────────────────────────────────────────────────────────── 
    
@login_required
def list_Booking_user(request):
    bookings = models.Booking.objects.filter(
        user=request.user
    ).order_by('-booking_date')

    # All booking ka auto status check
    for booking in bookings:
        booking.auto_update_status()

    # Fresh data
    booking = models.Booking.objects.filter(
        user=request.user
    ).order_by('-booking_date')

    return render(request, 'userapp/list_Booking_user.html', {'booking': booking})


# ── Update Booking For User ────────────────────────────────────────────────────────────

def update_Booking(request, id):
    booking1 = get_object_or_404(models.Booking, id=id)
    vehicles = Vehicle.objects.all()
    rental_locations = admin_models.RentalLocation.objects.all()
    status_choices = models.Booking.BOOKING_STATUS_CHOICES

    next_url = request.POST.get('next') or request.GET.get('next') or 'list_Booking_user'

    if request.method == 'POST':
        form = forms.BookingForm(request.POST, instance=booking1)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = booking1.user
            booking.total_hours = int(float(form.cleaned_data.get('total_hours') or 0))
            booking.total_amount = booking1.total_amount 
            booking.vehicle = booking1.vehicle  
            booking.save()
            messages.success(request, f"Booking #{id} updated successfully!")
            return redirect(next_url)  
        else:
            messages.error(request, "Please fix the errors below.")
            print(form.errors)  

    else:
        form = forms.BookingForm(instance=booking1)

    return render(request, 'userapp/update_Booking.html', {
        'form': form,
        'booking1': booking1,
        'vehicles': vehicles,
        'rental_locations': rental_locations,
        'status_choices': status_choices,
        'next': next_url,
    })


# ── Delete Booking ──────────────────────────────────────────────────────────── 

def delete_booking(request, id):
    booking = get_object_or_404(models.Booking, id=id)
    booking.delete()
    messages.success(request, f"Booking #{id} deleted successfully!")
    return redirect('list_Booking_user')


# ── Cancel Booking (Rapido Style) ─────────────────────────────────────────────

def cancel_booking(request, id):
    booking = get_object_or_404(models.Booking, id=id)

    # ── Block if not cancellable ─────────────────────────────────────
    if not booking.can_cancel():
        messages.error(
            request,
            f"Booking #{id} cannot be cancelled. "
            f"Current status: {booking.booking_status}"
        )
        return redirect('list_Booking_user')

    form = forms.CancelBookingForm()

    if request.method == 'POST':
        form = forms.CancelBookingForm(request.POST)
        if form.is_valid():
            reason       = form.cleaned_data['cancel_reason']
            other_reason = form.cleaned_data.get('cancel_reason_other', '')
            refund       = booking.get_refund_amount() 

            # ── Apply cancellation ───────────────────────────────────
            booking.booking_status      = 'Cancelled'
            booking.cancel_reason       = reason
            booking.cancel_reason_other = other_reason if reason == 'other' else ''
            booking.cancelled_at        = timezone.now()
            booking.refund_amount       = refund
            booking.refund_status       = 'Pending' if refund > 0 else 'None'
            booking.save()

            if refund > 0:
                messages.success(
                    request,
                    f"Booking #{id} cancelled. "
                    f"₹{refund} refund will be processed shortly."
                )
            else:
                messages.success(
                    request,
                    f"Booking #{id} cancelled. No refund applicable."
                )
            return redirect('list_Booking_user')

    context = {
        'booking':        booking,
        'form':           form,
        'refund_preview': booking.get_refund_amount(),
    }
    return render(request, 'userapp/cancel_booking.html', context)


# ── Static Payment Workflow ───────────────────────────────────────────────────

@login_required
def pay_booking(request, id):
    booking = get_object_or_404(models.Booking, id=id, user=request.user)
    if booking.booking_status != 'Confirmed' or booking.payment_status == 'Paid':
        messages.error(request, "This booking is not eligible for payment right now.")
        return redirect('list_Booking_user')
        
    return render(request, 'userapp/payment.html', {'booking': booking})

@login_required
def process_payment(request, id):
    if request.method == 'POST':
        booking = get_object_or_404(models.Booking, id=id, user=request.user)
        if booking.booking_status == 'Confirmed' and booking.payment_status == 'Unpaid':
            booking.payment_status = 'Paid'
            booking.save()
            messages.success(request, f"Payment of ₹{booking.total_amount} successful for Booking #{booking.id}.")
            return redirect('booking_invoice', id=booking.id)
    return redirect('list_Booking_user')

@login_required
def booking_invoice(request, id):
    booking = get_object_or_404(models.Booking, id=id, user=request.user)
    if booking.payment_status != 'Paid':
        messages.error(request, "Invoice is only available for paid bookings.")
        return redirect('list_Booking_user')
        
    return render(request, 'userapp/invoice.html', {'booking': booking})

@login_required
def submit_feedback(request, id):
    booking = get_object_or_404(models.Booking, id=id, user=request.user)
    if booking.payment_status != 'Paid':
        messages.error(request, "You can only provide feedback after payment.")
        return redirect('list_Booking_user')
        
    if hasattr(booking, 'feedback'):
        messages.info(request, "You have already provided feedback for this booking.")
        return redirect('list_Booking_user')

    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        review = request.POST.get('review', '')
        
        models.Feedback.objects.create(
            booking=booking,
            vehicle=booking.vehicle,
            user=request.user,
            rating=rating,
            review=review
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('list_Booking_user')
        
    return render(request, 'userapp/feedback.html', {'booking': booking})

#Booking End       

def ecycle_page(request):
    vehicles = Vehicle.objects.all()
    context = {'vehicles': vehicles}
    return render(request, 'userapp/ecycle.html', context)

def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        admin_models.Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        return redirect('contact_page')
    
    return render(request, 'userapp/contact.html')

def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    related_vehicles = Vehicle.objects.filter(
        category=vehicle.category
    ).exclude(id=vehicle.id)[:4]
    
    feedbacks = models.Feedback.objects.filter(vehicle=vehicle).order_by('-created_at')
    
    context = {
        'vehicle': vehicle,
        'related_vehicles': related_vehicles,
        'feedbacks': feedbacks,
    }
    return render(request, 'userapp/vehicle_detail.html', context)

def service_page(request):
    return render(request,'userapp/service.html')

def why_choose_page(request):
    return render(request,'userapp/why_choose.html')

def testimonial_page(request):
    return render(request,'userapp/testimonial.html')


#Login Start
User = get_user_model()


# ================= REGISTER =================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'User'
            user.is_approved = False
            user.registration_ip = request.META.get('REMOTE_ADDR')
            user.save()
            messages.success(request, "Registration successful! Wait for admin approval.")
            return redirect('user_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = RegisterForm()

    return render(request, 'userapp/register.html', {'form': form})


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == 'Admin':
                login(request, user)
                return redirect('index')
            elif user.role == 'User' and user.is_approved:
                login(request, user)
                return redirect('home_page')
            else:
                messages.warning(request, "Your account is pending admin approval!")
        else:
            messages.error(request, "Invalid Username or Password!")

    return render(request, 'userapp/login.html')


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    request.session.flush()
    messages.info(request, "Logged out successfully!")
    return redirect('user_login')


# ================= ADMIN DASHBOARD =================
@login_required
def admin_dashboard(request):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized access!")
        return redirect('user_login')

    all_users = User.objects.exclude(role='Admin')
    approved_users = User.objects.filter(is_approved=True, role='User')
    pending_users = User.objects.filter(is_approved=False, role='User')

    return render(request, 'userapp/dashboard_admin.html', {
        'all_users': all_users,
        'approved_users': approved_users,
        'rejected_users': pending_users, 
    })


# ================= USER DASHBOARD =================
@login_required
def user_dashboard(request):
    return render(request, 'userapp/dashboard_user.html')


# ================= APPROVE USER =================
@login_required
def approve_user(request, user_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized action!")
        return redirect('user_login') 

    user = get_object_or_404(User, id=user_id)

    if user.role == 'Admin':
        messages.warning(request, "Cannot approve Admin!")
        return redirect('admin_dashboard')

    user.is_approved = True
    user.save()
    messages.success(request, f"{user.username} approved!")
    return redirect('admin_dashboard')


# ================= REJECT USER =================
@login_required
def reject_user(request, user_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized action!")
        return redirect('user_login')

    user = get_object_or_404(User, id=user_id)

    if user.role == 'Admin':
        messages.warning(request, "Cannot reject Admin!")
        return redirect('admin_dashboard')

    user.is_approved = False
    user.save()
    messages.error(request, f"{user.username} rejected!")
    return redirect('admin_dashboard')

# Login End 


# User Profile Start  

# ================= VIEW PROFILE =================
@login_required
def profile_view(request):
    return render(request, 'userapp/profile.html', {'user': request.user})


# ================= EDIT PROFILE =================
User = get_user_model()

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Use User instead of CustomUser
            old_image = User.objects.get(pk=request.user.pk).profile_image
            new_image = form.cleaned_data.get('profile_image')

            if new_image and old_image and old_image != new_image:
                if os.path.isfile(old_image.path):
                    os.remove(old_image.path)

            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_view')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'userapp/profile.html', {'form': form, 'edit_mode': True})


# ================= DELETE PROFILE IMAGE =================
@login_required
def delete_profile_image(request):
    if request.method == 'POST':
        user = request.user
        if user.profile_image:
            # Delete file from disk
            image_path = user.profile_image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
            # Clear from DB
            user.profile_image = None
            user.save(update_fields=['profile_image'])
            messages.success(request, "Profile photo removed.")
        else:
            messages.info(request, "No profile image to remove.")
    return redirect('profile_edit')

# User Profile End

# ── Start Booking (Random Vehicle) ─────────────────────────────────────────────
def start_booking(request):
    vehicles = Vehicle.objects.all()

    if vehicles.exists():
        vehicle = random.choice(vehicles)
        return redirect('booking_page', id=vehicle.id)
    else:
        return redirect('home')

# ══════════════════════════════════════════════════════
# E-CYCLE TRACKING
# ══════════════════════════════════════════════════════

from app_modules.adminapp.models import CycleTracking, RentalLocation

@login_required
def tracking_page(request, booking_id):
    """
    Main tracking page for user — shows:
    1. Their active booking details
    2. Cycle current status & location on map
    3. All rental locations on map
    """
    booking = get_object_or_404(
        models.Booking,
        id=booking_id,
        user=request.user
    )

    # Get or create tracking record for this vehicle 
    tracking, created = CycleTracking.objects.get_or_create(
        vehicle=booking.vehicle,
        defaults={
            'cycle_status': 'available',
            'battery_level': 100,
            'current_location_name': booking.pickup_location,
        }
    )

    # Auto-update status based on booking status
    if booking.booking_status == 'Ongoing':
        tracking.cycle_status = 'in_use'
        tracking.save()
    elif booking.booking_status in ['Completed', 'Cancelled']:
        tracking.cycle_status = 'available'
        tracking.save()
    elif booking.booking_status == 'Confirmed':
        tracking.cycle_status = 'available'
        tracking.save()

    # Get all rental locations with coordinates for map
    all_locations = RentalLocation.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

    # Try to get pickup location coordinates from RentalLocation
    pickup_location = RentalLocation.objects.filter(
        location_name__icontains=booking.pickup_location
    ).first()
    dropoff_location = RentalLocation.objects.filter(
        location_name__icontains=booking.dropoff_location
    ).first()

    # Journey progress calculation
    status_steps = ['Pending', 'Confirmed', 'Ongoing', 'Completed']
    try:
        current_step = status_steps.index(booking.booking_status) + 1
    except ValueError:
        current_step = 0

    context = {
        'booking': booking,
        'tracking': tracking,
        'all_locations': all_locations,
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'current_step': current_step,
        'total_steps': len(status_steps),
        'progress_pct': int((current_step / len(status_steps)) * 100),
    }
    return render(request, 'userapp/tracking.html', context)


@login_required
def tracking_status_api(request, booking_id):
    """
    AJAX endpoint — returns latest tracking status as JSON
    Frontend polls this every 15 seconds
    """
    booking = get_object_or_404(
        models.Booking,
        id=booking_id,
        user=request.user
    )
    try:
        tracking = booking.vehicle.tracking
    except CycleTracking.DoesNotExist:
        return JsonResponse({'error': 'No tracking data'}, status=404)

    status_steps = ['Pending', 'Confirmed', 'Ongoing', 'Completed']
    try:
        step = status_steps.index(booking.booking_status) + 1
    except ValueError:
        step = 0

    return JsonResponse({
        'booking_status': booking.booking_status,
        'cycle_status': tracking.cycle_status,
        'battery_level': tracking.battery_level,
        'current_lat': float(tracking.current_latitude) if tracking.current_latitude else None,
        'current_lng': float(tracking.current_longitude) if tracking.current_longitude else None,
        'current_location_name': tracking.current_location_name or '',
        'last_updated': tracking.last_updated.strftime('%d %b %Y, %I:%M %p'),
        'progress_pct': int((step / len(status_steps)) * 100),
        'vehicle_name': booking.vehicle.vehicle_name,
        'pickup': booking.pickup_location,
        'dropoff': booking.dropoff_location,
        'start_time': str(booking.start_time),
        'end_time': str(booking.end_time),
        'total_hours': booking.total_hours,
    })


@login_required
def all_cycles_map(request):
    """
    Public map — shows all available cycles and rental station locations
    """
    all_locations = RentalLocation.objects.all()
    all_vehicles  = CycleTracking.objects.select_related('vehicle').all()

    context = {
        'all_locations': all_locations,
        'all_vehicles': all_vehicles,
    }
    return render(request, 'userapp/cycles_map.html', context)


#page not found
def custom_404(request, exception=None):
    return render(request, "userapp/404.html", status=404)
