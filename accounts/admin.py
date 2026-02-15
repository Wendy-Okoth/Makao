
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('is_landlord', 'is_tenant', 'phone_number')} ),
        )

admin.site.register(User, CustomUserAdmin)
