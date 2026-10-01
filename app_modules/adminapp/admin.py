from django.contrib import admin
from app_modules.adminapp import models

# Register your models here.

#City
admin.site.register(models.City)

#Vehicle Type
admin.site.register(models.Vehicle_type)

#Category
admin.site.register(models.Category)

#Vehicle
admin.site.register(models.Vehicle)

#RentalLocation
admin.site.register(models.RentalLocation) 

#Contact
admin.site.register(models.Contact)