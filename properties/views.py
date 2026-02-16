from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Property
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

# 1. Public List: See all available houses
class PropertyListView(ListView):
    model = Property
    template_name = 'property_list.html'
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(is_available=True).order_by('-created_at')

# 2. Public Detail: 3D Tour & Info
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'

# 3. Landlord: Their own listings
class LandlordDashboardView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'landlord_dashboard.html'
    context_object_name = 'my_properties'

    def get_queryset(self):
        if not self.request.user.is_landlord:
            raise PermissionDenied 
        return Property.objects.filter(landlord=self.request.user).order_by('-created_at')

# 4. Landlord: Add new property
class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Property
    template_name = 'property_form.html'
    fields = ['title', 'description', 'location', 'price', 'virtual_tour_url']
    success_url = reverse_lazy('landlord-dashboard')

    def test_func(self):
        return self.request.user.is_landlord

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        return super().form_valid(form)