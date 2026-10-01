from django import forms
from app_modules.adminapp import models

class city_form(forms.ModelForm):
    class Meta:
        model = models.City
        fields = '__all__' 
        
class vehicletype_form(forms.ModelForm):
    class Meta:
        model = models.Vehicle_type
        fields = '__all__'

class category_form(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = '__all__'
        
class vehicle_form(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        fields = '__all__'
        
class rentallocation_form(forms.ModelForm):
    class Meta:
        model = models.RentalLocation
        fields = '__all__'