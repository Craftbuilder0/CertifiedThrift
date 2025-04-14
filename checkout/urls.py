from django.contrib import admin
from django.urls import path
from checkout import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.checkout_view, name='checkout_view'),
    path('checkout_process', views.checkout, name='checkout'),
    path('save-shipping-details', views.save_shipping_details, name='save_shipping_details'),
    path('success', views.payment_success, name='success'),
    path('cancle', views.payment_cancel, name='cancle'),
]
