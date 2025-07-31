from django.urls import path,include
from . import views



urlpatterns = [
    
    path('',views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('property_page', views.property_page, name='property_page'),
    path('prediction_page', views.prediction_page, name='prediction_page'),
    path('reg_page', views.reg_page, name='reg_page'),
    path('profile', views.profile, name='profile'),
  







    


]

