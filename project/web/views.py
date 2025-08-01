from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .ml_model import get_location_names, get_estimated_price
from django.contrib import messages


# Create your views here.

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')
    ob = property_table.objects.filter(status="accepted")
    return render(request, 'dashboard.html', {'val': ob})


def property_page(request, property_id):
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')
    property_obj = get_object_or_404(property_table, id=property_id)
    user_obj = property_obj.USER
    return render(request, 'property_page.html', {'property': property_obj, 'user': user_obj})


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




def reg_page(request):
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')
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
        # Set status to 'pending' regardless of form input
        status = 'pending'
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
        messages.success(request, "Property registered successfully! Status is pending.")
        return redirect('dashboard')  # Redirect to dashboard instead of reg_page
    return render(request, 'register.html')

def profile(request):
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    user_obj = user_table.objects.get(id=user_id)
    # Get all properties owned by this user
    properties = property_table.objects.filter(USER=user_obj)
    return render(request, 'profile.html', {'user': user_obj, 'properties': properties})



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
            request.session['username'] = user_obj.username
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
            # For demonstration, display the username and password (not secure for real apps)
            return HttpResponse(f"Your username: {login_obj.username}<br>Your password: {login_obj.password}")
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
            username=username,
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
    messages.success(request, "Property deleted successfully!")
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

