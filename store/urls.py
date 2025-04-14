from django.contrib import admin
from django.urls import path
from store import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.store_view, name='store'),
    path("product-page-<slug:slug>", views.product_view, name='product'),
    path('add_to_cart/<slug:slug>', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/<slug:slug>', views.update_cart, name='update_cart_item'),
    path('remove-from-cart/<slug:slug>', views.remove_from_cart, name='remove_from_cart'),
    path('cart', views.view_cart, name='cart'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]