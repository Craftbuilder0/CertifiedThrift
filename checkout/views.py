from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from store.models import *
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

# Create your views here.
def checkout_view(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    context = {
        'items': items,
        'order': order
    }
    return render(request, 'checkout/checkout.html', context)


@csrf_exempt # This is the way of handling post requets without updating the whole web
def save_shipping_details(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        zipcode = request.POST.get('postal_code')
        state = request.POST.get('state')
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = address,
            city = city,
            state = state,
            zipcode = zipcode            
        )
        return JsonResponse({'message': 'Shipping details saved'})

    return JsonResponse({'error': 'Invalid request'}, status=400)
        

@login_required
@require_POST
def checkout(request):
    cart = get_object_or_404(Order, user=request.user)

    return redirect('payment')
  

def payment_success(request):
    return render(request, 'Errors/success.html')


def payment_cancel(request):
    return render(request, 'Errors/cancel.html')

