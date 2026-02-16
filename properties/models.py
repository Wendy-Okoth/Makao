from django.db import models
from django.conf import settings

class Property(models.Model):
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='my_properties'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    virtual_tour_url = models.URLField(max_length=500, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} - {self.location}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500) 

    def __str__(self):
        return f"Image for {self.property.title}"