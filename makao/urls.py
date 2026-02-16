"""
URL configuration for makao project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from properties.views import (
    PropertyListView, 
    PropertyCreateView, 
    PropertyDetailView, 
    LandlordDashboardView,
    TenantDashboardView,
    TenantExploreView
)
from accounts.views import signup_view, login_success_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('listings/', PropertyListView.as_view(), name='property-list'),
    path('dashboard/', LandlordDashboardView.as_view(), name='landlord-dashboard'),
    path('property/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('property/add/', PropertyCreateView.as_view(), name='property-add'), 
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('login-success/', login_success_redirect, name='login-success'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('tenant/dashboard/', TenantDashboardView.as_view(), name='tenant-dashboard'),
    path('tenant/explore/', TenantExploreView.as_view(), name='tenant-explore'),
]
  
