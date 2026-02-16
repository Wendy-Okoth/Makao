import re
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def signup_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone_number')
        passw = request.POST.get('password')
        conf_passw = request.POST.get('confirm_password')
        
        is_landlord = request.POST.get('is_landlord') == 'True'
        is_tenant = request.POST.get('is_tenant') == 'True'

        # 1. Validation: Passwords match
        if passw != conf_passw:
            messages.error(request, "Passwords do not match!")
            return render(request, 'signup.html')

        # 2. Validation: Role selection
        if not is_landlord and not is_tenant:
            messages.error(request, "Please select whether you are a Tenant or a Landlord.")
            return render(request, 'signup.html')

        # 3. Validation: Password Strength (Regex)
        # At least 8 chars, 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Char
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_regex, passw):
            messages.error(request, "Password is too weak. Please follow the requirements.")
            return render(request, 'signup.html')

        # 4. Validation: Check if Username or Email exists
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "This username is already taken.")
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'signup.html')

        # 5. Success: Create the user
        try:
            user = User.objects.create_user(
                username=u_name, 
                email=email, 
                password=passw,
                phone_number=phone,
                is_landlord=is_landlord,
                is_tenant=is_tenant
            )
            login(request, user)
            
            if user.is_landlord:
                return redirect('landlord-dashboard')
            return redirect('property-list')
        except Exception as e:
            messages.error(request, f"Something went wrong: {e}")
            
    return render(request, 'signup.html')


@login_required
def login_success_redirect(request):
    """
    Redirects users based on their role after login.
    """
    if request.user.is_landlord:
        return redirect('landlord-dashboard')
    else:
        return redirect('property-list')