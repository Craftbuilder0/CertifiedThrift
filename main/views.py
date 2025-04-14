from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from store.models import *
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# Create your views here.

def home_view(request):
    # Get all the products from the database
    product = products.objects.all()
    # Get the latest 3 product to showcase in the "Recent Products" Section
    product = product.order_by('-created_at')[:3]
    # Featured product(not added)
    return render(request, 'general/index.html', {'products': product,
                                                  'slides': product[:3]})

def about_view(request):
    return render(request, 'general/about.html')

@login_required
def account_view(request):
    customer, created = Customer.objects.get_or_create(user=request.user, defaults={'email': request.user.email, 'name': request.user.username})
    address = ShippingAddress.objects.all()

    if request.method == 'POST':
        if 'old_password' in request.POST:
            # Password change form submitted
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, 'Your password was successfully updated.')
                return redirect('account')  # Redirect to avoid resubmission
            
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'delete_address_id' in request.POST:
            address_id = request.POST.get('delete_address_id')
            ShippingAddress.objects.filter(id=address_id, customer=customer).delete()
            return redirect('account')
        
        elif 'name' in request.POST and 'email' in request.POST:
            new_name = request.POST.get('name')
            new_email = request.POST.get('email')

            # Update Django's user model
            request.user.username = new_name
            request.user.email = new_email
            request.user.save()

            # Also update Customer model
            customer.name = new_name
            customer.email = new_email
            customer.save()

            messages.success(request, "Profile information updated successfully.")
            return redirect('account')
        
        else:
            # Handle other forms here
            password_form = PasswordChangeForm(user=request.user)  # Still pass it to the template
    else:
        password_form = PasswordChangeForm(user=request.user)

    context = {
        'user': request.user,
        'orders': Order.objects.filter(customer=customer),
        'password_form': password_form,
        'addresses': address
    }
    return render(request, 'general/account.html', context)


'''
These are all user authintication related part and are almost same for every webs
'''
def user_login(request):
    next_url = request.GET.get('next', 'home')  # fallback to 'home'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect(next_url)
        else:
            messages.error(request, 'Sorry credentials!')
            return redirect('login')
    else:  
        return render(request, "registration/login.html", {"title": "Login"})
    

def user_logout(request):
    logout(request)
    return redirect('home')


def user_signup(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        # Create inactive user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # Generate token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        activation_link = f"http://{domain}{reverse('verify_email', kwargs={'uidb64': uid, 'token': token})}"

        # Send email
        subject = 'Activate your account'
        message = f'Hi {user.username},\nPlease click the link below to verify your email:\n{activation_link}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        messages.success(request, 'Account created! Please check your email to verify your account.')
        return redirect('login')
    else:
        return render(request, 'registration/signup.html')
    

def pleaseLogin(request):
    return render(request, 'Errors/pleaseLogin.html')


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('signup')
    

def custom_page_not_found_view(request, exception):
    return render(request, 'Errors/404.html', status=404)