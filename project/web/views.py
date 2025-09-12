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





def prediction_page(request):
    if not request.session.get('user_id'):
        return redirect('login')
    locations = get_location_names()
    price = None
    if request.method == 'POST':
        location = request.POST.get('location')
        sqft = float(request.POST.get('sqft'))
        bhk = int(request.POST.get('bhk'))
        bath = int(request.POST.get('bath'))
        price = get_estimated_price(location, sqft, bhk, bath)
    return render(request, 'prediction_page.html', {'locations': locations, 'price': price})




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


# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         try:
#             login_obj = login_table.objects.get(username=username, password=password)
#             user_obj = user_table.objects.get(LOGIN=login_obj)
#             # Set session variables
#             request.session['user_id'] = user_obj.id
#             request.session['username'] = login_obj.username
#             return redirect('dashboard')
#         except (login_table.DoesNotExist, user_table.DoesNotExist):
#             return HttpResponse("Invalid credentials")
#     return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check for admin credentials first (hardcoded)
        if username == 'admin' and password == '123':
            # Create a dummy user object for admin
            class AdminUser:  # Create a dummy class
                def __init__(self, username):
                    self.username = username
            class AdminLogin:
                def __init__(self, username):
                    self.username = username
            admin_login = AdminLogin(username='admin')
            admin_user = AdminUser(username='admin')
            request.session['user_id'] = -1  # Use -1 or any non-existent id
            request.session['username'] = 'admin'
            return redirect('admindashboard')
        else:
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



def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user_obj = user_table.objects.get(email=email)
            login_obj = user_obj.LOGIN

            subject = 'Your Login Credentials'
            message = f"Username: {login_obj.username}\nPassword: {login_obj.password}"
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            send_mail(subject, message, from_email, to_email, fail_silently=False)

            return HttpResponse("Email sent!")

        except user_table.DoesNotExist:
            return HttpResponse("Email not found.")
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
        if login_table.objects.filter(username=username).exists():
            return HttpResponse("Username already exists.")
        if user_table.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")

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


def profile_search(request):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    user_obj = user_table.objects.get(id=user_id)

    query = request.GET.get('q', '')
    area = request.GET.get('area', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    properties = property_table.objects.filter(USER=user_obj)

    if query:
        properties = properties.filter(
            Q(property_name__icontains=query) |
            Q(street__icontains=query) |
            Q(description__icontains=query)
        )
    if area:
        properties = properties.filter(area__icontains=area)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)

    return render(request, 'profile.html', {
        'user': user_obj,
        'properties': properties,
        'query': query,
        'area': area,
        'min_price': min_price,
        'max_price': max_price,
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