from django.contrib import admin
from django.urls import path
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home_view, name='home'),
    path("about", views.about_view, name='about'),
    path("account", views.account_view, name='account'),
    path("login", views.user_login, name='login'),
    path("logout", views.user_logout, name='logout'),
    path("signup", views.user_signup, name='signup'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path("pleaseLogin", views.pleaseLogin, name='pleaseLogin'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
]
