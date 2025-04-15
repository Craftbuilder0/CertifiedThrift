from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

# Create your models here.

# Model for defining product's category
class category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Model for storing products in the database
class products(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    image = CloudinaryField('image') #models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(default=datetime.today())
    available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically generate slug based on product name if slug is not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
	        
    
# Customer model - Same as user model but more formal way of handling user in ecommerce website
class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name


# Order model - you can think of it as the mail cart that stores all the product
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    
    # Order tracking
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='processing')
    
    def __str__(self):
        return str(self.id)   

    # Custom function for extracting total values for products
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total 

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
	

# Orderitem model - This holds the product's quantity, status and more on certain cases
class OrderItem(models.Model):
    product = models.ForeignKey(products, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True) 

    # Custom function for extracting total values for product's price x quantity
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


# ShippingAddress model - This is used to storing the shipping informations
class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=True)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
     

class Review(models.Model):
    product = models.ForeignKey(products, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}⭐"


# Creating a form(best practice is to make a forms.py file)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']