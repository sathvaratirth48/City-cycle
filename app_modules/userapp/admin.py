from django.contrib import admin
from app_modules.userapp import models
from django.contrib.auth.admin import UserAdmin
from app_modules.userapp.models import CustomUser
from django.utils.html import format_html, mark_safe 

# Register your models here.

#login  

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('username', 'email', 'role', 'is_approved', 'is_kyc_verified', 'kyc_preview', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_kyc_verified')

    def aadhaar_preview(self, obj):
        if obj.aadhaar_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="200" style="border-radius:6px; border:1px solid #ccc;"/>'
                '</a>', obj.aadhaar_image.url, obj.aadhaar_image.url
            )
        return "❌ Not Uploaded"
    aadhaar_preview.short_description = "Aadhaar Card"

    def pan_preview(self, obj):
        if obj.pan_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="200" style="border-radius:6px; border:1px solid #ccc;"/>'
                '</a>', obj.pan_image.url, obj.pan_image.url
            )
        return "❌ Not Uploaded"
    pan_preview.short_description = "PAN Card"

    def other_doc_preview(self, obj):
        if obj.other_document_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="200" style="border-radius:6px; border:1px solid #ccc;"/>'
                '</a>', obj.other_document_image.url, obj.other_document_image.url
            )
        return "❌ Not Uploaded"
    other_doc_preview.short_description = "Other Document"

    def kyc_preview(self, obj):
        links = []
        if obj.aadhaar_image:
            links.append(f'<a href="{obj.aadhaar_image.url}" target="_blank">📄 Aadhaar</a>')
        if obj.pan_image:
            links.append(f'<a href="{obj.pan_image.url}" target="_blank">💳 PAN</a>')
        if obj.other_document_image:
            links.append(f'<a href="{obj.other_document_image.url}" target="_blank">📁 Other</a>')
        return mark_safe(" | ".join(links)) if links else "❌ No Docs"
    kyc_preview.short_description = "KYC Docs"


    readonly_fields = ('aadhaar_preview', 'pan_preview', 'other_doc_preview', 'kyc_preview')

    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('role', 'is_approved', 'phone_number', 'profile_image', 'address', 'date_of_birth')
        }),
        ('KYC Documents', {
            'fields': (
                'aadhaar_number', 'aadhaar_preview',
                'pan_number', 'pan_preview',
                'other_document_image', 'other_doc_preview',
                'is_kyc_verified',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Info', {
            'fields': ('role', 'is_approved', 'phone_number', 'address', 'date_of_birth', 'profile_image'),
        }),
        ('KYC Documents', {
            'fields': (
                'aadhaar_number', 'aadhaar_image',
                'pan_number', 'pan_image',
                'other_document_image',
                'is_kyc_verified',
            ),
        }),
    )
    

#Booking 
admin.site.register(models.Booking)