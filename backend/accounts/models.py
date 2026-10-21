from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model where email is unique and can be used for authentication.
    """
    email = models.EmailField(unique=True, verbose_name='email address')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username or self.email


class PasswordResetOTP(models.Model):
    """
    Stores OTPs generated for forgot password / password reset verification.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='password_reset_otps'
    )
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    reset_token = models.CharField(max_length=64, blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        indexes = [
            models.Index(fields=['email', 'otp']),
            models.Index(fields=['reset_token']),
        ]

    def __str__(self):
        return f"OTP {self.otp} for {self.email} ({'Used' if self.is_used else ('Verified' if self.is_verified else 'Pending')})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired

    @classmethod
    def generate_otp(cls, user, email):
        import secrets
        from datetime import timedelta
        from django.utils import timezone

        # Mark any previous unused OTPs for this user as used
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        code = f"{secrets.randbelow(900000) + 100000}"
        token = secrets.token_urlsafe(32)
        expires = timezone.now() + timedelta(minutes=10)

        return cls.objects.create(
            user=user,
            email=email.lower().strip(),
            otp=code,
            reset_token=token,
            expires_at=expires,
        )

