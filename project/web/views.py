from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def property_page(request):
    return render(request, 'property_page.html')

def prediction_page(request):
    return render(request, 'prediction_page.html')

def reg_page(request):
    return render(request, 'register.html')  

def profile(request):
    return render(request, 'profile.html')





#Funtions for the website





