from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('login-otp/', views.login_otp_view, name='login_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-otp/', views.password_reset_otp_view, name='password_reset_otp'),
    path('reset-password/', views.password_reset_otp_view, name='reset_password'),
    path('login-history/', views.login_history_view, name='login_history'),
]
