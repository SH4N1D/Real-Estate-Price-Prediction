from django.db import models

# Create your models here.
class login_table(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class user_table(models.Model):
    LOGIN = models.ForeignKey(login_table, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_images/', default='default.jpg')
    phone = models.CharField(max_length=15)
    place = models.CharField(max_length=100)

class property_table(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    image1 = models.ImageField(upload_to='property_images/', default='default_property.jpg')
    image2 = models.ImageField(upload_to='property_images/', default='default_property.jpg')
    image3 = models.ImageField(upload_to='property_images/', default='default_property.jpg')
    image4 = models.ImageField(upload_to='property_images/', default='default_property.jpg')
    bed = models.CharField(max_length=100)
    bath = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    description = models.CharField(max_length=500)


