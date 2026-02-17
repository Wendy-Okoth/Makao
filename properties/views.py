from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Property, Favorite
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

# 1. PUBLIC: Gallery
class PropertyListView(ListView):
    model = Property
    template_name = 'public_gallery.html' 
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(is_available=True).order_by('-created_at')

# 2. SHARED: Detail View
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'

# 3. TENANT: Main Hub
class TenantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved_count'] = Favorite.objects.filter(user=self.request.user).count()
        return context

# 4. TENANT: Logged-in Marketplace
class TenantExploreView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'view_property.html'
    context_object_name = 'properties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorited_ids'] = Favorite.objects.filter(
                user=self.request.user
            ).values_list('property_id', flat=True)
        return context

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

# 7. LOGIC: Favorite Toggle
@login_required
def toggle_favorite(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    
    if not created:
        favorite.delete()
        
    return redirect(request.META.get('HTTP_REFERER', 'tenant-explore'))

# 8. TENANT: Favorites List
class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'tenant_favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('property')