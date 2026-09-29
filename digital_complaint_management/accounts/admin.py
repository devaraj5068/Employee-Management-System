from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LoginHistory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_verified', 'account_status', 'is_staff')
    list_filter = ('role', 'account_status', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Information', {
            'fields': ('role', 'phone_number', 'address', 'profile_picture', 'account_status', 'is_verified', 'otp_code', 'otp_expiry')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Information', {
            'fields': ('role', 'phone_number', 'address', 'email')
        }),
    )

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('username_attempted', 'user', 'ip_address', 'status', 'failure_reason', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('username_attempted', 'ip_address', 'failure_reason')
    readonly_fields = ('user', 'username_attempted', 'ip_address', 'user_agent', 'timestamp', 'status', 'failure_reason')


from .models import OTPVerification

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'is_verified', 'attempts', 'expires_at', 'created_at', 'used_at')
    list_filter = ('purpose', 'is_verified', 'created_at')
    search_fields = ('email', 'user__username')
    readonly_fields = ('otp_hash', 'created_at', 'last_sent_at', 'used_at')
