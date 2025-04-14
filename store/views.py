# Importing...........
from django.shortcuts import render, redirect, get_object_or_404
from store.models import products, category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from store.models import *
from django.http import HttpResponse

# Create your views here.

def store_view(request):
    # Get all products from the database
    product = products.objects.all()
    
    # Filters
    category_name = request.GET.get('category', None)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')

    if category_name:
        # Get the category object from the category name
        try:
            category_obj = category.objects.get(name=category_name)
            # Now filter products based on the category object
            product = products.objects.filter(category=category_obj)

        except category.DoesNotExist:
            product = products.objects.none()
    if min_price:
        product = product.filter(price__gte=min_price)
    if max_price:
        product = product.filter(price__lte=max_price)
    if search:
        product = product.filter(name__icontains=search)

    # Sort by latest
    product = product.order_by('-created_at')
    
    return render(request, 'store/store.html', {'products': product, 'category': category.objects.all()})


def product_view(request, slug):
    # Getting the specific product using the passed-in slug
    product = products.objects.get(slug=slug)
    # Returning the values to the template
    context = {
        'product': product, 
        'category': category.objects.all(), 
        'related_products': products.objects.all()
    }
    return render(request, 'store/products.html', context)


@login_required
def view_cart(request):
    # Get the customer via user(In the models.py there's a OneToOne relationship between two)
    customer, created = Customer.objects.get_or_create(user=request.user, defaults={'email': request.user.email, 'name': request.user.username}) 
    # Get the order via customer id or create a new Order. 
    order, created = Order.objects.get_or_create(customer=customer, complete=False)  
    # Using reverse relationships(Created when using foreing key in model relaitonship) in Django to get all related OrderItem objects for a given Order
    items = order.orderitem_set.all()
    # Passing all the datas to the template
    context = {
        'items': items,
        'order': order
    }
    return render(request, 'store/cart.html', context)


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(products, slug=slug) # Get the Product using slug from the model

    # Get or create a Customer for the logged-in user
    
    customer, created = Customer.objects.get_or_create(user=request.user, defaults={'email': request.user.email, 'name': request.user.username})

    # Get or create an active order for the customer accessed via customer model
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Get or create an order item for the product accessed via order model
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Increase quantity by 1
    order_item.quantity += 1
    order_item.save()

    return redirect('cart') 


@login_required
def update_cart(request, slug):  # This is for updating the quantity of each product in the cart
    # If submitted
    if request.method == "POST":
        # Access the OrderItem model using the product slug
        item = get_object_or_404(OrderItem, product__slug=slug)
        quantity = request.POST.get('quantity')

        try:
            quantity = int(quantity)
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
        except (ValueError, TypeError):
            # Handle invalid quantity input gracefully
            pass

    return redirect('cart')


@login_required
def remove_from_cart(request, slug):
    if request.method == "POST":
        # Get the first matching OrderItem for this user and product
        order_item = OrderItem.objects.filter(
            product__slug=slug,
            user=request.user,
            ordered=False
        ).first()

        if order_item:
            order_item.delete()

    return redirect('cart')
