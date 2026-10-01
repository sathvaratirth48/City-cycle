from django.forms.widgets import FileInput
from django import forms
from app_modules.userapp import models
from .models import CustomUser
from datetime import date
import re

#Login Start

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    aadhaar_number = forms.CharField(
        max_length=12,
        required=True,
        label="Aadhaar Number"
    )
    aadhaar_image = forms.ImageField(
        required=True,
        label="Aadhaar Card Image"
    )
    pan_number = forms.CharField(
        max_length=10,
        required=False,
        label="PAN Number"
    )
    pan_image = forms.ImageField(
        required=False,
        label="PAN Card Image"
    )
    other_document_image = forms.ImageField(
        required=False,
        label="Other Document"
    )
    phone_number = forms.CharField(
        max_length=10,
        required=False,
        label="Phone Number"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email',
            'phone_number',
            'address',
            'date_of_birth',
            'aadhaar_number', 'aadhaar_image',
            'pan_number', 'pan_image', 'other_document_image',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': '2019-12-31'
                }
            ),
        }

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number', '').strip()

        if not re.fullmatch(r'\d{12}', aadhaar):
            raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")

        if CustomUser.objects.filter(aadhaar_number=aadhaar).exists():
            raise forms.ValidationError("This Aadhaar number is already registered.")

        return aadhaar

    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number', '').strip().upper()

        if not pan:
            return None 

        if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', pan):
            raise forms.ValidationError("Invalid PAN format. Correct format: ABCDE1234F")

        if CustomUser.objects.filter(pan_number=pan).exists():
            raise forms.ValidationError("This PAN number is already registered.")

        return pan
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()

        if not phone:
            return phone  

        # Exactly 10 digits, no letters or symbols
        if not re.fullmatch(r'\d{10}', phone):
            raise forms.ValidationError("Phone number exactly 10 digits hona chahiye.")

        return phone
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')

        if dob and dob > date(2019, 12, 31):
            raise forms.ValidationError(
                "Please enter a valid Date of Birth. Year must be 2019 or earlier."
            )
        return dob

    def clean(self):
        cleaned_data = super().clean()

        # Password match check
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password1')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        # PAN cross-validation
        pan_number = cleaned_data.get('pan_number')
        pan_image = cleaned_data.get('pan_image')
        if pan_number and not pan_image:
            self.add_error('pan_image', "Please upload PAN card image if you provide PAN number.")
        if pan_image and not pan_number:
            self.add_error('pan_number', "Please enter PAN number if you upload PAN card image.")

        return cleaned_data
        
#Login End

#User Profile Start
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'phone_number',
            'address',
            'date_of_birth',
            'profile_image',
        ]
        widgets = {
            'profile_image': FileInput(),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': '2019-12-31'
                }
            ),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')

        if dob and dob > date(2019, 12, 31):
            raise forms.ValidationError(
                "Please enter a valid Date of Birth. Year must be 2019 or earlier."
            )

        return dob

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image and hasattr(image, 'size'):
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size must be under 5MB.")
        return image


#User Profile End

#Booking Start  
class BookingForm(forms.ModelForm):
    start_time = forms.TimeField(
        input_formats=['%I:%M %p', '%H:%M'] 
    )
    end_time = forms.TimeField(
        input_formats=['%I:%M %p', '%H:%M']
    )
    booking_date = forms.DateField(
        input_formats=['%d-%m-%Y', '%Y-%m-%d']
    )
    total_hours = forms.FloatField(required=False)
    
    class Meta:
        model = models.Booking
        fields = [
        'pickup_location',
        'dropoff_location',
        'adult',
        'child',
        'start_time',
        'end_time',
        'total_hours',
        'total_amount',
        'booking_date',
        'special_requests',
        ]


# ── Cancel Booking Form ───────────────────────────────────────
class CancelBookingForm(forms.Form):
    cancel_reason = forms.ChoiceField(
        choices=models.Booking.CANCEL_REASON_CHOICES,
        widget=forms.RadioSelect(),
        label="Reason for Cancellation"
    )
    cancel_reason_other = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class':       'form-control',
            'rows':        3,
            'placeholder': 'Please describe your reason...'
        }),
        label="Other Reason"
    )

    def clean(self):
        cleaned_data = super().clean()
        reason       = cleaned_data.get('cancel_reason')
        other_reason = cleaned_data.get('cancel_reason_other')

        if reason == 'other' and not other_reason.strip():
            raise forms.ValidationError("Please describe your reason for cancellation.")
        return cleaned_data
    
#Booking End 