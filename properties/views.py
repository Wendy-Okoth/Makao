
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Property

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