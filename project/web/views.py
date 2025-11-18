from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from .ml_model import get_location_names, get_estimated_price
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import json
from django.shortcuts import render, redirect
from .models import property_table
from django.conf import settings
import os
from django.http import JsonResponse
import smtplib
from email.mime.text import MIMEText

# Create your views here.

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    ob = property_table.objects.filter(status="accepted").exclude(USER__id=user_id)
    return render(request, 'dashboard.html', {'val': ob})




# def property_page(request, property_id):
#     # Check if user is logged in
#     if not request.session.get('user_id'):
#         return redirect('login')
#     property_obj = get_object_or_404(property_table, id=property_id)
#     user_obj = property_obj.USER
#     return render(request, 'property_page.html', {'property': property_obj, 'user': user_obj})


def property_page(request, property_id):
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')

    property_obj = get_object_or_404(property_table, id=property_id)
    user_obj = property_obj.USER

    # Get predicted price
    predicted_price = get_estimated_price(
        property_obj.area,  # Assuming 'area' is the location
        float(property_obj.area),  # Assuming 'area' is total sqft
        int(property_obj.bed),
        int(property_obj.bath)
    )

    return render(request, 'property_page.html', {
        'property': property_obj,
        'user': user_obj,
        'predicted_price': predicted_price,
    })





# def prediction_page(request):
#     if not request.session.get('user_id'):
#         return redirect('login')
#     locations = get_location_names()
#     price = None
#     if request.method == 'POST':
#         location = request.POST.get('location')
#         sqft = float(request.POST.get('sqft'))
#         bhk = int(request.POST.get('bhk'))
#         bath = int(request.POST.get('bath'))
#         price = get_estimated_price(location, sqft, bhk, bath)
#     return render(request, 'prediction_page.html', {'locations': locations, 'price': price})



# In your views.py file

# def prediction_page(request):
#     if not request.session.get('user_id'):
#         return redirect('login')
    
#     locations = get_location_names()
#     price = None
    
#     if request.method == 'POST':
#         # --- Get all form inputs ---
#         location = request.POST.get('location')
#         sqft = float(request.POST.get('sqft') or 0)
#         bhk = int(request.POST.get('bhk') or 0)
#         bath = int(request.POST.get('bath') or 0)
#         age = int(request.POST.get('age') or 0)
#         property_type = request.POST.get('ptype')
        
#         # 1. Get the new 'amenities' level from the form
#         amenities_level = int(request.POST.get('amenities') or 1)
        
#         # --- Price Calculation ---
#         initial_price = get_estimated_price(location, sqft, bhk, bath)
        
#         if initial_price is not None:
#             # --- Define all adjustment factors ---
            
#             # Property Type Factors
#             type_factors = {
#                 'Apartment': 1.0,
#                 'Independent House': 1.10,
#                 'Villa': 1.25,
#             }
#             property_type_factor = type_factors.get(property_type, 1.0)
            
#             # 2. Amenities Factors
#             amenity_factors = {
#                 0: 0.95,  # 5% less for no amenities
#                 1: 1.0,   # Baseline for basic amenities
#                 2: 1.05,  # 5% more for standard
#                 3: 1.15,  # 15% more for luxury
#             }
#             amenities_factor = amenity_factors.get(amenities_level, 1.0) # Default to 1.0

#             # Age Depreciation Factor
#             depreciation_rate = 0.007
#             depreciation_factor = max(0, 1 - (age * depreciation_rate))
            
#             # 3. Apply ALL factors to the initial price
#             final_price = initial_price * depreciation_factor * property_type_factor * amenities_factor
            
#             price = round(final_price, 2)
            
#     return render(request, 'prediction_page.html', {'locations': locations, 'price': price})



def prediction_page(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    locations = get_location_names()
    price = None
    
    if request.method == 'POST':
        # --- Get all form inputs ---
        location = request.POST.get('location')
        sqft = float(request.POST.get('sqft') or 0)
        property_type = request.POST.get('ptype')
        connectivity_level = int(request.POST.get('connectivity') or 1)

        bhk = int(request.POST.get('bhk') or 1)
        bath = int(request.POST.get('bath') or 1)
        initial_price = get_estimated_price(location, sqft, bhk, bath)
        
        if initial_price is not None:
            if property_type == 'Plot':
                # UPDATED: 0.40 is too low for Bengaluru. 0.70 (70%) is more realistic 
                # as land value dominates the total property cost.
                plot_factor = 0.70
                
                connectivity_factors = {
                    0: 0.90, 
                    1: 1.0, 
                    2: 1.10, 
                    # UPDATED: Increased to 1.25 to reflect strong impact of metro/IT hubs.
                    3: 1.25  
                }
                connectivity_factor = connectivity_factors.get(connectivity_level, 1.0)
                final_price = initial_price * plot_factor * connectivity_factor
            
            else: # Logic for Apartment, House, Villa
                age = int(request.POST.get('age') or 0)
                amenities_level = int(request.POST.get('amenities') or 1)
                floor_level = request.POST.get('floor_level', 'Middle')
                quality_level = int(request.POST.get('quality', 0))

                # Depreciation mapping - your values are logical heuristics, so they are kept.
                rate_mapping = {
                    0: 0.007,  # Basic property depreciates at 0.7% per year
                    1: 0.005,  # Standard property at 0.5%
                    2: 0.003,  # Prime property at 0.3%
                    3: 0.001,  # Luxury/Renovated property at a very low 0.1%
                }
                dynamic_depreciation_rate = rate_mapping.get(quality_level, 0.007)
                depreciation_factor = max(0, 1 - (age * dynamic_depreciation_rate))

                # --- Other existing factors ---
                # Your type factors are reasonable.
                type_factors = {'Apartment': 1.0, 'Independent House': 1.10, 'Villa': 1.25}
                property_type_factor = type_factors.get(property_type, 1.0)
                
                amenity_factors = {
                    0: 0.95, 
                    1: 1.0, 
                    2: 1.05, 
                    # UPDATED: Increased to 1.20 as luxury amenities add significant value.
                    3: 1.20 
                }
                amenities_factor = amenity_factors.get(amenities_level, 1.0)
                
                connectivity_factors = {
                    0: 0.90, 
                    1: 1.0, 
                    2: 1.10, 
                    # UPDATED: Increased to 1.25 for properties, matching the plot logic.
                    3: 1.25 
                }
                connectivity_factor = connectivity_factors.get(connectivity_level, 1.0)
                
                # Your floor factors are perfect.
                floor_factor = 1.0
                if property_type == 'Apartment':
                    floor_level_factors = {'Lower': 0.98, 'Middle': 1.0, 'Higher': 1.05}
                    floor_factor = floor_level_factors.get(floor_level, 1.0)

                # 4. Calculate Final Price
                final_price = initial_price * depreciation_factor * property_type_factor * amenities_factor * connectivity_factor * floor_factor
            
            price = round(final_price, 2)
            
    return render(request, 'prediction_page.html', {'locations': locations, 'price': price, 'lakh': 'Lakh'})




# def reg_page(request):
#     # Check if user is logged in
#     if not request.session.get('user_id'):
#         return redirect('login')
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         user_obj = user_table.objects.get(id=user_id)
#         property_name = request.POST.get('property_name')
#         street = request.POST.get('street')
#         area = request.POST.get('sqft')
#         bed = request.POST.get('bed')
#         bath = request.POST.get('bath')
#         description = request.POST.get('description')
#         price = request.POST.get('price')
#         # Set status to 'pending' regardless of form input
#         status = 'pending'
#         image1 = request.FILES.get('image1')
#         image2 = request.FILES.get('image2')
#         image3 = request.FILES.get('image3')
#         image4 = request.FILES.get('image4')

#         property_table.objects.create(
#             USER=user_obj,
#             property_name=property_name,
#             street=street,
#             area=area,
#             bed=bed,
#             bath=bath,
#             description=description,
#             price=price,
#             status=status,
#             image1=image1,
#             image2=image2,
#             image3=image3,
#             image4=image4
#         )
#         messages.success(request, "Property registered successfully! Status is pending.")
#         return redirect('dashboard')  # Redirect to dashboard instead of reg_page
#     return render(request, 'register.html')



def reg_page(request):
    if not request.session.get('user_id'):
        return redirect('login')

    # Load street options from columns.json
    columns_path = os.path.join(settings.BASE_DIR, 'web', 'ml_artifacts', 'columns.json')
    with open(columns_path, 'r') as f:
        data = json.load(f)
        streets = data['data_columns']

    # Filter out the first three elements
    streets = streets[3:]

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_obj = user_table.objects.get(id=user_id)
        property_name = request.POST.get('property_name')
        street = request.POST.get('street')
        area = request.POST.get('sqft')
        bed = request.POST.get('bed')
        bath = request.POST.get('bath')
        description = request.POST.get('description')
        price = request.POST.get('price')
        status = 'accepted'
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        property_table.objects.create(
            USER=user_obj,
            property_name=property_name,
            street=street,
            area=area,
            bed=bed,
            bath=bath,
            description=description,
            price=price,
            status=status,
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4
        )
        messages.success(request, "Property registered successfully!")
        return redirect('dashboard')

    # The view now only handles the initial GET request for the page
    return render(request, 'register.html', {
        'streets': streets,
        'street_value': request.GET.get('street', ''),
        'area_value': request.GET.get('sqft', ''),
        'bed_value': request.GET.get('bed', ''),
        'bath_value': request.GET.get('bath', ''),
    })







def profile(request):
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    user_obj = user_table.objects.get(id=user_id)
    # Get all properties owned by this user
    properties = property_table.objects.filter(USER=user_obj)
    return render(request, 'profile.html', {'user': user_obj, 'properties': properties})

def admindashboard_view(request):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')

    # Check if the user is the admin (based on user_id)
    if user_id == -1:  # Assuming -1 is the admin user_id
        properties = property_table.objects.filter(status='pending')
        return render(request, 'admindashboard.html', {'properties': properties})
    else:
        return HttpResponse("Unauthorized access")







#Funtions for the website


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            login_obj = login_table.objects.get(username=username, password=password)
            user_obj = user_table.objects.get(LOGIN=login_obj)
            # Set session variables
            request.session['user_id'] = user_obj.id
            request.session['username'] = login_obj.username
            return redirect('dashboard')
        except (login_table.DoesNotExist, user_table.DoesNotExist):
            return HttpResponse("Invalid credentials")
    return render(request, 'login.html')


# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         # Check for admin credentials first (hardcoded)
#         if username == 'admin' and password == '123':
#             # Create a dummy user object for admin
#             class AdminUser:  # Create a dummy class
#                 def __init__(self, username):
#                     self.username = username
#             class AdminLogin:
#                 def __init__(self, username):
#                     self.username = username
#             admin_login = AdminLogin(username='admin')
#             admin_user = AdminUser(username='admin')
#             request.session['user_id'] = -1  # Use -1 or any non-existent id
#             request.session['username'] = 'admin'
#             return redirect('admindashboard')
#         else:
#             try:
#                 login_obj = login_table.objects.get(username=username, password=password)
#                 user_obj = user_table.objects.get(LOGIN=login_obj)
#                 # Set session variables
#                 request.session['user_id'] = user_obj.id
#                 request.session['username'] = login_obj.username
#                 return redirect('dashboard')
#             except (login_table.DoesNotExist, user_table.DoesNotExist):
#                 return HttpResponse("Invalid credentials")
#     return render(request, 'login.html')



# def forgotpassword(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         try:
#             user_obj = user_table.objects.get(email=email)
#             login_obj = user_obj.LOGIN

#             subject = 'Your Login Credentials'
#             message = f"Username: {login_obj.username}\nPassword: {login_obj.password}"
#             from_email = settings.EMAIL_HOST_USER
#             to_email = [email]

#             send_mail(subject, message, from_email, to_email, fail_silently=False)

#             return HttpResponse("Email sent!")

#         except user_table.DoesNotExist:
#             return HttpResponse("Email not found.")
#     return render(request, 'forgotpassword.html')

def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        try:
            login_obj = login_table.objects.get(username=username)
            user_obj = user_table.objects.get(LOGIN=login_obj, email=email)

            subject = 'Your Login Credentials'
            message = f"Username: {login_obj.username}\nPassword: {login_obj.password}"
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            try:
                if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                    return HttpResponse("Email settings are not configured properly.")

                gmail = smtplib.SMTP('smtp.gmail.com', 587)
                gmail.ehlo()
                gmail.starttls()
                gmail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['To'] = email
                msg['From'] = settings.EMAIL_HOST_USER
                gmail.send_message(msg)
                return HttpResponse("Email sent!")

            except Exception as e:
                return HttpResponse(f"Error sending email: {e}")

        except (login_table.DoesNotExist, user_table.DoesNotExist):
            return HttpResponse("Invalid username or email.")
    return render(request, 'forgotpassword.html')



def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('phone')
        place = request.POST.get('place')
        image = request.FILES.get('image')

        if password != confirm_password:
            return HttpResponse("Passwords do not match.")
        if login_table.objects.filter(username__iexact=username).exists():
            return HttpResponse("Username already exists.")
        if user_table.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if user_table.objects.filter(phone=phone).exists():
            return HttpResponse("Phone number already exists.")

        login_obj = login_table.objects.create(username=username, password=password)
        user_obj = user_table.objects.create(
            LOGIN=login_obj,
            email=email,
            fname=fname,
            lname=lname,
            phone=phone,
            place=place,
            image=image if image else 'default.jpg'
        )
        return redirect('login')
    return render(request, 'signup.html')


def logout_view(request):
    # Clear session
    request.session.flush()
    return redirect('home')

def delete_property(request, property_id):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    property_obj = get_object_or_404(property_table, id=property_id, USER__id=user_id)
    property_obj.delete()
    return redirect('profile')


def dashboard_search(request):
    if not request.session.get('user_id'):
        return redirect('login')

    location = request.GET.get('location', '')
    area = request.GET.get('area', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    bedrooms = request.GET.get('bedrooms', '')
    bathrooms = request.GET.get('bathrooms', '')

    properties = property_table.objects.filter(status="accepted")

    if location:
        properties = properties.filter(Q(street__icontains=location))
    if area:
        properties = properties.filter(area__icontains=area)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if bedrooms:
        properties = properties.filter(bed=bedrooms)
    if bathrooms:
        properties = properties.filter(bath=bathrooms)

    return render(request, 'dashboard.html', {
        'val': properties,
        'location': location,
        'area': area,
        'min_price': min_price,
        'max_price': max_price,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
    })


# def profile_search(request):
#     if not request.session.get('user_id'):
#         return redirect('login')
#     user_id = request.session.get('user_id')
#     user_obj = user_table.objects.get(id=user_id)

#     location = request.GET.get('location', '')
#     area = request.GET.get('area', '')
#     min_price = request.GET.get('min_price', '')
#     max_price = request.GET.get('max_price', '')
#     bedrooms = request.GET.get('bedrooms', '')
#     bathrooms = request.GET.get('bathrooms', '')

#     properties = property_table.objects.filter(USER=user_obj)

#     if location:
#         properties = properties.filter(Q(street__icontains=location))
#     if area:
#         properties = properties.filter(area__icontains=area)
#     if min_price:
#         properties = properties.filter(price__gte=min_price)
#     if max_price:
#         properties = properties.filter(price__lte=max_price)
#     if bedrooms:
#         properties = properties.filter(bed=bedrooms)
#     if bathrooms:
#         properties = properties.filter(bath=bathrooms)

#     return render(request, 'profile.html', {
#         'user': user_obj,
#         'val': properties,
#         'location': location,
#         'area': area,
#         'min_price': min_price,
#         'max_price': max_price,
#         'bedrooms': bedrooms,
#         'bathrooms': bathrooms,
#     })


def profile_search(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session.get('user_id')
    user_obj = user_table.objects.get(id=user_id)

    query = request.GET.get('q', '').strip()
    area = request.GET.get('area', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    bedrooms = request.GET.get('bedrooms', '').strip()
    bathrooms = request.GET.get('bathrooms', '').strip()

    properties = property_table.objects.filter(USER=user_obj)

    # Keyword search
    if query:
        properties = properties.filter(
            Q(property_name__icontains=query) |
            Q(street__icontains=query) |
            Q(description__icontains=query)
        )

    # Area filter
    if area:
        properties = properties.filter(area__icontains=area)

    # Bedroom and Bathroom filters
    if bedrooms:
        properties = properties.filter(bed__icontains=bedrooms)
    if bathrooms:
        properties = properties.filter(bath__icontains=bathrooms)

    # Price filter (convert to number safely)
    def safe_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    min_price_val = safe_int(min_price)
    max_price_val = safe_int(max_price)

    if min_price_val is not None:
        properties = [p for p in properties if safe_int(p.price) and safe_int(p.price) >= min_price_val]
    if max_price_val is not None:
        properties = [p for p in properties if safe_int(p.price) and safe_int(p.price) <= max_price_val]

    return render(request, 'profile.html', {
        'user': user_obj,
        'properties': properties,
        'query': query,
        'area': area,
        'min_price': min_price,
        'max_price': max_price,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
    })


def admin_property_update(request, property_id):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')

    # Check if the user is the admin (based on user_id)
    if user_id == -1:
        property_obj = get_object_or_404(property_table, id=property_id)
        return render(request, 'admin_property_update.html', {'property': property_obj})
    else:
        return HttpResponse("Unauthorized access")

def update_property_status(request, property_id):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')

    # Check if the user is the admin (based on user_id)
    if user_id == -1:
        property_obj = get_object_or_404(property_table, id=property_id)
        if request.method == 'POST':
            status = request.POST['status']
            property_obj.status = status
            property_obj.save()
            return redirect('admindashboard')
        else:
            return HttpResponse("Invalid request")
    else:
        return HttpResponse("Unauthorized access")





# At the top of your_app/views.py, add these imports
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

# --- Add these three views ---

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Use filter().first() to avoid exception if user doesn't exist
        user = user_table.objects.filter(email=email).first()

        if not user:
            messages.error(request, 'No user found with this email.')
            return redirect('forgot_password')

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        try:
            # Send OTP via email
            send_mail(
                'Your Password Reset OTP',
                f'Your OTP to reset the password is: {otp}',
                None,  # Uses DEFAULT_FROM_EMAIL from settings
                [email],
                fail_silently=False, # Make sure this is False to raise errors
            )

            # Store OTP and email in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            # Add a flag indicating OTP step started
            request.session['otp_sent'] = True

            # Redirect to OTP verification page
            return redirect('verify_otp')

        except Exception as e:
            # Display the actual error if email sending fails
            # Print to console for debugging
            # Stay on the same page to show the error
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        
        if user_otp == stored_otp:
            # OTP is correct, "promote" the session
            request.session['can_reset_password'] = True
            return redirect('set_new_password')
        else:
            # messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
            
    # If it's a GET request, check if they should be here
    if not request.session.get('reset_otp'):
        return redirect('forgot_password')

    return render(request, 'verify_otp.html')


def set_new_password(request):
    # Check if user is allowed to be here
    if not request.session.get('can_reset_password'):
        # messages.error(request, 'Please verify your OTP first.')
        return redirect('verify_otp')

    if request.method == 'POST':
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('set_new_password')
        
        email = request.session.get('reset_email')
        if not email:
            return redirect('forgot_password')

        try:
            user = user_table.objects.get(email=email)
            user.LOGIN.password=new_password  
            user.LOGIN.save()
            
            # Clean up session data
            request.session.pop('reset_otp', None)
            request.session.pop('reset_email', None)
            request.session.pop('can_reset_password', None)
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'An error occurred. User not found.')
            return redirect('login')

    return render(request, 'set_new_password.html')