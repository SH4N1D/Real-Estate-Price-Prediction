from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404



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
    # Check if user is logged in
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'prediction_page.html')


from django.contrib import messages

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
    return redirect('login')

def delete_property(request, property_id):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    property_obj = get_object_or_404(property_table, id=property_id, USER__id=user_id)
    property_obj.delete()
    messages.success(request, "Property deleted successfully!")
    return redirect('profile')




