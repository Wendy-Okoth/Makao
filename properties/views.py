from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Property
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

# 1. PUBLIC: Gallery for anyone (Public Navbar)
class PropertyListView(ListView):
    model = Property
    template_name = 'public_gallery.html' 
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(is_available=True).order_by('-created_at')

# 2. SHARED: Detail View (Used by both Tenant & Landlord)
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'

# 3. TENANT: Main Hub
class TenantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_dashboard.html'

# 4. TENANT: Logged-in Marketplace
class TenantExploreView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'view_property.html'
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(is_available=True).order_by('-created_at')

# 5. LANDLORD: Dashboard
class LandlordDashboardView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'landlord_dashboard.html'
    context_object_name = 'my_properties'

    def get_queryset(self):
        if not self.request.user.is_landlord:
            raise PermissionDenied 
        return Property.objects.filter(landlord=self.request.user).order_by('-created_at')

# 6. LANDLORD: Add Form
class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Property
    template_name = 'property_list.html' 
    fields = ['title', 'description', 'location', 'price', 'virtual_tour_url']
    success_url = reverse_lazy('landlord-dashboard')

    def test_func(self):
        return self.request.user.is_landlord

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        return super().form_valid(form)