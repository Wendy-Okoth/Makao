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
# Import your views directly
from properties.views import PropertyListView, PropertyDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Homepage: Points directly to the view, no include needed!
    path('', PropertyListView.as_view(), name='property-list'),
    
    # Detail page
    path('property/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
]
