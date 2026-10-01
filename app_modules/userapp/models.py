from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime

# Create your models here.

#Login Start  

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    is_approved = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    aadhaar_number = models.CharField(
        max_length=12, blank=True, null=True, unique=True
    )
    pan_number = models.CharField(
        max_length=10, blank=True, null=True, unique=True
    )

    aadhaar_image = models.ImageField(upload_to='kyc/aadhaar/', null=True, blank=True)
    pan_image = models.ImageField(upload_to='kyc/pan/', null=True, blank=True)
    other_document_image = models.ImageField(upload_to='kyc/other/', null=True, blank=True)

    is_kyc_verified = models.BooleanField(default=False)
    registration_ip = models.GenericIPAddressField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.pan_number:
            self.pan_number = None
        if not self.aadhaar_number:
            self.aadhaar_number = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
#Login End 

# Booking Start         
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    BOOKING_STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Ongoing',   'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    CANCEL_REASON_CHOICES = [
        ('change_of_plans',     'Change of Plans'),
        ('wrong_booking',       'Booked by Mistake'),
        ('driver_not_assigned', 'Driver Not Assigned'),
        ('long_wait',           'Wait Time Too Long'),
        ('emergency',           'Personal Emergency'),
        ('other',               'Other'),
    ]

    REFUND_STATUS_CHOICES = [
        ('None',      'None'),
        ('Pending',   'Pending'),
        ('Processed', 'Processed'),
    ]

    # ── Your existing fields (unchanged) ────────────────────────────
    vehicle          = models.ForeignKey('adminapp.Vehicle', on_delete=models.CASCADE)
    pickup_location  = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    adult            = models.IntegerField()
    child            = models.IntegerField()
    start_time       = models.TimeField()
    end_time         = models.TimeField()
    total_hours      = models.IntegerField()
    total_amount     = models.IntegerField()
    booking_status   = models.CharField(max_length=255, choices=BOOKING_STATUS_CHOICES, default='Pending')
    booking_date     = models.DateField()
    special_requests = models.TextField(blank=True, null=True)
    payment_status   = models.CharField(
        max_length=20,
        choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')],
        default='Unpaid'
    )
    
    confirmed_at = models.DateTimeField(null=True, blank=True)
    def auto_update_status(self):
        """
        Confirmed hone ke baad:
        2 min → Ongoing
        4 min → Completed
        """
        if self.booking_status in ['Cancelled', 'Completed']:
            return False  # Kuch mat karo

        if not self.confirmed_at:
            return False  # Confirmed time nahi hai

        now = timezone.now()
        diff = (now - self.confirmed_at).total_seconds()

        changed = False

        if diff >= 240 and self.booking_status != 'Completed':
            # 4 min baad → Completed
            self.booking_status = 'Completed'
            self.vehicle.is_available = 'yes'
            self.vehicle.save()
            try:
                tracking = self.vehicle.tracking
                tracking.cycle_status = 'available'
                tracking.current_location_name = self.dropoff_location
                tracking.save()
            except:
                pass
            changed = True

        elif diff >= 120 and self.booking_status == 'Confirmed':
            # 2 min baad → Ongoing
            self.booking_status = 'Ongoing'
            self.vehicle.is_available = 'no'
            self.vehicle.save()
            try:
                tracking = self.vehicle.tracking
                tracking.cycle_status = 'in_use'
                tracking.current_location_name = self.pickup_location
                tracking.save()
            except:
                pass
            changed = True

        if changed:
            self.save()

        return changed
    

    # ── New cancellation fields ──────────────────────────────────────
    cancel_reason       = models.CharField(max_length=50,  choices=CANCEL_REASON_CHOICES, blank=True, null=True)
    cancel_reason_other = models.TextField(blank=True, null=True)
    cancelled_at        = models.DateTimeField(blank=True, null=True)
    refund_amount       = models.IntegerField(default=0)
    refund_status       = models.CharField(max_length=20,  choices=REFUND_STATUS_CHOICES, default='None')

    # ── Helper methods ─────────────────────────────────────────────── 
    def can_cancel(self):
        """Only Pending or Confirmed rides can be cancelled."""
        return self.booking_status in ['Pending', 'Confirmed']

    def get_refund_amount(self):
        """
        Rapido-style refund policy:
          Pending   → 100% refund  (driver not yet assigned)
          Confirmed → 50%  refund  (driver assigned)
          Anything else → no refund
        """
        if self.booking_status == 'Pending':
            return self.total_amount            # 100%
        elif self.booking_status == 'Confirmed':
            return self.total_amount // 2       # 50%
        return 0

    def __str__(self):
        return f"Booking #{self.id} | {self.vehicle} | {self.booking_status}"
        
    @property
    def has_feedback(self):
        return hasattr(self, 'feedback')

# Booking End

# Feedback Start
class Feedback(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="feedback")
    vehicle = models.ForeignKey('adminapp.Vehicle', on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5) # 1 to 5
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.vehicle} by {self.user.username}"
# Feedback End