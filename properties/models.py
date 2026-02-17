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

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property') # Prevents double-favoriting

class Inquiry(models.Model):
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_inquiries')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField(default="I am interested in this property. Please contact me with more details.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry by {self.tenant.username} for {self.property.title}"

class Message(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']