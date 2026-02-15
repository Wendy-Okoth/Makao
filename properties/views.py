
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Property
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

# 1. For Consumers: See all available houses
class PropertyListView(ListView):
    model = Property
    template_name = 'property_list.html'
    context_object_name = 'properties'

    def get_queryset(self):
        # Only show houses that haven't been paid for yet
        return Property.objects.filter(is_available=True).order_by('-created_at')

# 2. For Consumers: See details and the Virtual Tour
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'


class LandlordDashboardView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'landlord_dashboard.html'
    context_object_name = 'my_properties'

    def get_queryset(self):
        # Only show properties belonging to the logged-in user
        if not self.request.user.is_landlord:
            raise PermissionDenied # Only landlords allowed!
        return Property.objects.filter(landlord=self.request.user)
    


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    template_name = 'property_form.html'
    fields = ['title', 'description', 'location', 'price', 'virtual_tour_url']
    success_url = reverse_lazy('landlord-dashboard')

    def form_valid(self, form):
        # Automatically set the landlord to the currently logged-in user
        form.instance.landlord = self.request.user
        return super().form_valid(form)