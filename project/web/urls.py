from django.urls import path,include
from . import views



urlpatterns = [
    
    path('', views.login, name='login'),
    path('home',views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('property/<int:property_id>/', views.property_page, name='property_page'),
    path('prediction_page', views.prediction_page, name='prediction_page'),
    path('reg_page', views.reg_page, name='reg_page'),
    path('profile', views.profile, name='profile'),
    path('forgotpassword', views.forgotpassword, name='forgotpassword'),
    path('signup', views.signup, name='signup'),


# Functions for the website

    path('delete_property/<int:property_id>/', views.delete_property, name='delete_property'),
    path('logout/', views.logout_view, name='logout'),








    


]

