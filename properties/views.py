from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Property, Favorite
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Inquiry , Message
from django.db.models import Count
from django.db.models import Q

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

class TenantExploreView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'view_property.html'
    context_object_name = 'properties'

    def get_queryset(self):
        queryset = Property.objects.filter(is_available=True)
        
        # Get parameters from GET request
        location_query = self.request.GET.get('location')
        max_price = self.request.GET.get('max_price')
        category_query = self.request.GET.get('category')
        sort_by = self.request.GET.get('sort')

        # Apply Search Filters
        if location_query:
            queryset = queryset.filter(location__icontains=location_query)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if category_query:
            queryset = queryset.filter(category=category_query)

        # Apply Sorting Logic
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorited_ids'] = Favorite.objects.filter(
                user=self.request.user
            ).values_list('property_id', flat=True)
        return context
    
# 5. LANDLORD: Dashboard
class LandlordDashboardView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'landlord_dashboard.html'
    context_object_name = 'my_properties'

    def get_queryset(self):
        if not self.request.user.is_landlord:
            raise PermissionDenied 
        return Property.objects.filter(landlord=self.request.user)\
                               .annotate(inquiry_count=Count('inquiries'))\
                               .order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This powers the "Pending Inquiries" stat at the top of your dashboard
        context['total_inquiries'] = Inquiry.objects.filter(
            property__landlord=self.request.user
        ).count()
        return context

# 6. LANDLORD: Add Form
class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Property
    template_name = 'property_list.html' 
    fields = ['title', 'category','description', 'location', 'price', 'virtual_tour_url']
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

class InquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = 'tenant_inquiries.html'
    context_object_name = 'inquiries'

    def get_queryset(self):
        return Inquiry.objects.filter(tenant=self.request.user).select_related('property')

@login_required
def send_inquiry(request, property_id):
    if request.method == "POST":
        property_obj = get_object_or_404(Property, id=property_id)
        message_text = request.POST.get('message', '').strip()
        
        if not message_text:
            message_text = "I am interested in this property. Please contact me."

        Inquiry.objects.create(
            tenant=request.user,
            property=property_obj,
            message=message_text
        )
        # Optional: add a success message
        return redirect('property-detail', pk=property_id)
    return redirect('tenant-explore')

class PropertyInquiryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Inquiry
    template_name = 'landlord_property_inquiries.html'
    context_object_name = 'inquiries'

    def test_func(self):
        # Ensure only the owner of the property can see its inquiries
        property_obj = get_object_or_404(Property, id=self.kwargs['property_id'])
        return property_obj.landlord == self.request.user

    def get_queryset(self):
        return Inquiry.objects.filter(property_id=self.kwargs['property_id']).select_related('tenant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = get_object_or_404(Property, id=self.kwargs['property_id'])
        return context
    
@login_required
def chat_view(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if request.user != inquiry.tenant and request.user != inquiry.property.landlord:
        raise PermissionDenied

    # --- NEW: Mark messages as Read ---
    inquiry.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == "POST":
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                inquiry=inquiry,
                sender=request.user,
                text=content
            )
            return redirect('chat-view', inquiry_id=inquiry.id)

    chat_messages = inquiry.messages.all()
    return render(request, 'chat.html', {
        'inquiry': inquiry,
        'chat_messages': chat_messages
    })

def get_queryset(self):
    return Property.objects.filter(landlord=self.request.user)\
        .annotate(
            inquiry_count=Count('inquiries'),
            # Count unread messages that weren't sent by the landlord
            unread_count=Count('inquiries__messages', filter=Q(inquiries__messages__is_read=False) & ~Q(inquiries__messages__sender=self.request.user))
        ).order_by('-created_at')