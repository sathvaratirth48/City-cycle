from django.db import models

# Create your models here.

# City  
class City(models.Model):
    city_name = models.CharField(max_length=255)
    created_at = models.DateField()
    
#Vehicle Type
class Vehicle_type(models.Model):
    type_name = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    
#Category 
class Category(models.Model):
    Vehicle_type = models.ForeignKey(Vehicle_type, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateField()
    
#Vehicle 
class Vehicle(models.Model):
    vehicle_name = models.CharField(max_length=255)
    vehicle_type = models.ForeignKey(Vehicle_type, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    price_per_hour =models.IntegerField()
    description = models.TextField()
    is_available = models.CharField(max_length=255)
    created_at = models.DateField()
    vehicle_img = models.ImageField(upload_to='vehicle_image/',null=True,blank=True)
    
    def __str__(self):
        return self.vehicle_name  


#Rental Location
class RentalLocation(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    created_at = models.DateField()
    latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='e.g. 23.022505')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='e.g. 72.571362')

    def __str__(self):
        return f"{self.location_name} ({self.city.city_name})"

# CycleTracking — software-based live status + location
class CycleTracking(models.Model):
    STATUS_CHOICES = [
        ('available',   'Available'),
        ('in_use',      'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('charging',    'Charging'),
    ]

    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='tracking')
    cycle_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    battery_level     = models.IntegerField(default=100, help_text='Battery % (0-100)')
    current_location_name = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_name} — {self.cycle_status}"

    class Meta:
        verbose_name = 'Cycle Tracking'
        verbose_name_plural = 'Cycle Trackings'
    
#Contact
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()