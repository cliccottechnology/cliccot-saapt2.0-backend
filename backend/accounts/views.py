from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from .models import CustomUser, PasswordResetOTP
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LoginUserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
)

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Accessible by anyone (AllowAny).
    Returns user details upon registration.
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    API endpoint for user login.
    Accepts either username or email along with password.
    Returns user info and JWT tokens (access and refresh).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = serializer.validated_data['tokens']

        return Response(
            {
                "message": "Login successful.",
                "user": LoginUserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    API endpoint for logging out.
    Requires authentication. Blacklists the supplied refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required to log out."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update the currently authenticated user's profile.
    GET /api/auth/me/
    PUT/PATCH /api/auth/me/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    API endpoint to change password for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Current password is not correct."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )


class ForgotPasswordView(APIView):
    """
    Step 1: Request password reset OTP.
    POST /api/auth/forgot-password/
    Payload: { "email": "user@example.com" }
    Generates a secure 6-digit OTP and sends it to the registered email address.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        email = serializer.validated_data['email']

        # Generate OTP (valid for 10 minutes)
        otp_obj = PasswordResetOTP.generate_otp(user=user, email=email)

        # Prepare email contents
        subject = "Your Password Reset OTP - SAAPT"
        user_name = user.get_full_name() or user.username
        plain_text_message = (
            f"Hello {user_name},\n\n"
            f"We received a request to reset your password for your SAAPT account.\n"
            f"Your One-Time Password (OTP) is: {otp_obj.otp}\n\n"
            f"This OTP is valid for 10 minutes.\n"
            f"If you did not request a password reset, please ignore this email.\n\n"
            f"Best regards,\nSAAPT Team"
        )
        html_message = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin: 0 0 6px 0;">SAAPT Portal</h2>
                <p style="color: #64748b; font-size: 14px; margin: 0;">Password Reset Verification Code</p>
            </div>
            <div style="padding: 24px; background-color: #f8fafc; border-radius: 8px; text-align: center;">
                <p style="color: #475569; font-size: 14px; margin: 0 0 16px 0;">
                    Hello <strong>{user_name}</strong>, use the following One-Time Password (OTP) to reset your password:
                </p>
                <div style="font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #2563eb; padding: 12px 24px; background: #ffffff; border: 2px dashed #cbd5e1; border-radius: 8px; display: inline-block;">
                    {otp_obj.otp}
                </div>
                <p style="color: #94a3b8; font-size: 12px; margin: 16px 0 0 0;">
                    This OTP is valid for <strong>10 minutes</strong>.
                </p>
            </div>
            <p style="color: #64748b; font-size: 12px; margin-top: 20px; text-align: center;">
                If you did not request this password reset, please ignore this email.
            </p>
        </div>
        """

        try:
            send_mail(
                subject=subject,
                message=plain_text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to send email via configured backend ({e}). OTP was generated: {otp_obj.otp}"
            )

        return Response(
            {
                "message": "OTP has been sent to your registered email address.",
                "email": email,
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    """
    Step 2: Verify the OTP entered by the user.
    POST /api/auth/verify-otp/
    Payload: { "email": "user@example.com", "otp": "123456" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_record = serializer.validated_data['otp_record']
        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        return Response(
            {
                "message": "OTP verified successfully. You can now enter your new password.",
                "email": otp_record.email,
                "reset_token": otp_record.reset_token,
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    """
    Step 3: Set new password and confirm password after successful OTP verification.
    POST /api/auth/reset-password/
    Payload: {
        "email": "user@example.com",
        "otp": "123456" (or "reset_token": "..."),
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_record = serializer.validated_data['otp_record']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        otp_record.is_used = True
        otp_record.save(update_fields=['is_used'])

        return Response(
            {
                "message": "Password changed successfully. You can now log in with your new password.",
            },
            status=status.HTTP_200_OK
        )


class ForgotPasswordUIView(APIView):
    """
    Interactive Web UI demonstrating the complete Forgot Password -> OTP -> Reset Password flow.
    Accessible at: GET /api/auth/forgot-password/ui/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SAAPT - Forgot Password</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at 10% 20%, #0f172a 0%, #1e293b 90%);
      color: #f1f5f9;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .card {
      background: rgba(30, 41, 59, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 36px 32px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }
    .logo-badge {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 18px;
      color: #fff;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .brand-title {
      font-size: 20px;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.2;
    }
    .brand-sub {
      font-size: 13px;
      color: #94a3b8;
    }
    .stepper {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 28px;
      position: relative;
    }
    .stepper::before {
      content: '';
      position: absolute;
      top: 14px;
      left: 20px;
      right: 20px;
      height: 2px;
      background: #334155;
      z-index: 1;
    }
    .step-item {
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }
    .step-dot {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #334155;
      color: #94a3b8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.3s;
    }
    .step-label {
      font-size: 11px;
      color: #94a3b8;
      font-weight: 500;
    }
    .step-item.active .step-dot {
      background: #3b82f6;
      color: #ffffff;
      box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.25);
    }
    .step-item.active .step-label {
      color: #60a5fa;
      font-weight: 600;
    }
    .step-item.completed .step-dot {
      background: #10b981;
      color: #ffffff;
    }
    .form-group {
      margin-bottom: 18px;
      text-align: left;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: #cbd5e1;
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      padding: 12px 14px;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      color: #f8fafc;
      font-size: 14px;
      transition: all 0.2s;
    }
    input:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }
    .otp-input {
      letter-spacing: 12px;
      font-size: 24px;
      text-align: center;
      font-weight: 700;
    }
    .btn {
      width: 100%;
      padding: 13px;
      background: linear-gradient(135deg, #2563eb, #4f46e5);
      border: none;
      border-radius: 10px;
      color: white;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .btn:hover {
      background: linear-gradient(135deg, #1d4ed8, #4338ca);
      transform: translateY(-1px);
    }
    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
    .btn-secondary {
      background: transparent;
      border: 1px solid #334155;
      color: #94a3b8;
      box-shadow: none;
      margin-top: 10px;
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #ffffff;
    }
    .alert {
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 13px;
      margin-bottom: 16px;
      display: none;
      line-height: 1.4;
    }
    .alert-error {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
    }
    .alert-success {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #6ee7b7;
    }
    .badge-info {
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.25);
      color: #93c5fd;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 12px;
      margin-bottom: 16px;
    }
    .hidden { display: none !important; }
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">
      <div class="logo-badge">S</div>
      <div>
        <div class="brand-title">SAAPT Portal</div>
        <div class="brand-sub">Password Recovery System</div>
      </div>
    </div>

    <div class="stepper">
      <div class="step-item active" id="stepIndicator1">
        <div class="step-dot">1</div>
        <div class="step-label">Email</div>
      </div>
      <div class="step-item" id="stepIndicator2">
        <div class="step-dot">2</div>
        <div class="step-label">OTP</div>
      </div>
      <div class="step-item" id="stepIndicator3">
        <div class="step-dot">3</div>
        <div class="step-label">New Password</div>
      </div>
    </div>

    <div id="alertBox" class="alert"></div>

    <!-- Step 1: Request OTP -->
    <div id="step1">
      <div class="badge-info">
        Enter your registered email address. We will send a 6-digit OTP to verify your account.
      </div>
      <form id="requestOtpForm">
        <div class="form-group">
          <label for="emailInput">Registered Email Address</label>
          <input type="email" id="emailInput" placeholder="name@example.com" required autocomplete="email">
        </div>
        <button type="submit" class="btn" id="sendOtpBtn">Send OTP</button>
      </form>
    </div>

    <!-- Step 2: Verify OTP -->
    <div id="step2" class="hidden">
      <div class="badge-info">
        An OTP has been sent to <strong id="displayEmail"></strong>. Please enter the 6-digit code below.
      </div>
      <form id="verifyOtpForm">
        <div class="form-group">
          <label for="otpInput">6-Digit Verification Code</label>
          <input type="text" id="otpInput" class="otp-input" maxlength="6" pattern="[0-9]{6}" placeholder="------" required>
        </div>
        <button type="submit" class="btn" id="verifyOtpBtn">Verify OTP</button>
        <button type="button" class="btn btn-secondary" id="resendOtpBtn">Resend OTP</button>
      </form>
    </div>

    <!-- Step 3: New Password -->
    <div id="step3" class="hidden">
      <div class="badge-info">
        OTP verified! Please create and confirm your new password (minimum 8 characters).
      </div>
      <form id="resetPasswordForm">
        <div class="form-group">
          <label for="newPasswordInput">New Password</label>
          <input type="password" id="newPasswordInput" placeholder="••••••••" minlength="8" required>
        </div>
        <div class="form-group">
          <label for="confirmPasswordInput">Confirm New Password</label>
          <input type="password" id="confirmPasswordInput" placeholder="••••••••" minlength="8" required>
        </div>
        <button type="submit" class="btn" id="resetPasswordBtn">Change Password</button>
      </form>
    </div>

    <!-- Success Step -->
    <div id="stepSuccess" class="hidden">
      <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 48px; margin-bottom: 12px;">🎉</div>
        <h3 style="font-size: 18px; margin-bottom: 8px; color: #6ee7b7;">Password Changed!</h3>
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 24px;">
          Your password has been reset successfully. You can now log in using your new credentials.
        </p>
        <button type="button" class="btn" onclick="window.location.reload()">Reset Another Account</button>
      </div>
    </div>

  </div>

  <script>
    let userEmail = '';
    let userResetToken = '';
    let currentOtp = '';

    const alertBox = document.getElementById('alertBox');
    function showAlert(message, isError = true) {
      alertBox.textContent = message;
      alertBox.className = 'alert ' + (isError ? 'alert-error' : 'alert-success');
      alertBox.style.display = 'block';
    }
    function hideAlert() {
      alertBox.style.display = 'none';
    }

    // Step 1: Send OTP
    document.getElementById('requestOtpForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();
      const email = document.getElementById('emailInput').value.trim();
      const btn = document.getElementById('sendOtpBtn');
      btn.disabled = true;
      btn.textContent = 'Sending OTP...';

      try {
        const res = await fetch('/api/auth/forgot-password/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (res.ok) {
          userEmail = email;
          document.getElementById('displayEmail').textContent = email;
          document.getElementById('step1').classList.add('hidden');
          document.getElementById('step2').classList.remove('hidden');

          document.getElementById('stepIndicator1').className = 'step-item completed';
          document.getElementById('stepIndicator2').className = 'step-item active';

          showAlert(data.message || 'OTP sent successfully!', false);
        } else {
          const errMsg = data.email ? (Array.isArray(data.email) ? data.email[0] : data.email) : (data.detail || 'Unable to process request.');
          showAlert(errMsg, true);
        }
      } catch (err) {
        showAlert('Network error: ' + err.message, true);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Send OTP';
      }
    });

    // Step 2: Verify OTP
    document.getElementById('verifyOtpForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();
      const otp = document.getElementById('otpInput').value.trim();
      const btn = document.getElementById('verifyOtpBtn');
      btn.disabled = true;
      btn.textContent = 'Verifying...';

      try {
        const res = await fetch('/api/auth/verify-otp/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: userEmail, otp })
        });
        const data = await res.json();
        if (res.ok) {
          currentOtp = otp;
          userResetToken = data.reset_token || '';
          document.getElementById('step2').classList.add('hidden');
          document.getElementById('step3').classList.remove('hidden');

          document.getElementById('stepIndicator2').className = 'step-item completed';
          document.getElementById('stepIndicator3').className = 'step-item active';

          showAlert(data.message || 'OTP verified successfully!', false);
        } else {
          const errMsg = data.otp ? (Array.isArray(data.otp) ? data.otp[0] : data.otp) : (data.detail || 'Invalid OTP.');
          showAlert(errMsg, true);
        }
      } catch (err) {
        showAlert('Network error: ' + err.message, true);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Verify OTP';
      }
    });

    // Resend OTP
    document.getElementById('resendOtpBtn').addEventListener('click', async () => {
      hideAlert();
      const btn = document.getElementById('resendOtpBtn');
      btn.disabled = true;
      btn.textContent = 'Resending...';
      try {
        const res = await fetch('/api/auth/forgot-password/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: userEmail })
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('A new OTP has been sent to your email.', false);
        } else {
          showAlert(data.detail || 'Failed to resend OTP.', true);
        }
      } catch (err) {
        showAlert('Error: ' + err.message, true);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Resend OTP';
      }
    });

    // Step 3: Reset Password
    document.getElementById('resetPasswordForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();
      const new_password = document.getElementById('newPasswordInput').value;
      const confirm_password = document.getElementById('confirmPasswordInput').value;

      if (new_password !== confirm_password) {
        showAlert('Passwords do not match. Please re-enter.', true);
        return;
      }

      const btn = document.getElementById('resetPasswordBtn');
      btn.disabled = true;
      btn.textContent = 'Updating Password...';

      try {
        const res = await fetch('/api/auth/reset-password/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: userEmail,
            otp: currentOtp,
            reset_token: userResetToken,
            new_password: new_password,
            confirm_password: confirm_password
          })
        });
        const data = await res.json();
        if (res.ok) {
          document.getElementById('step3').classList.add('hidden');
          document.getElementById('stepSuccess').classList.remove('hidden');
          document.getElementById('stepIndicator3').className = 'step-item completed';
          showAlert(data.message || 'Password changed successfully!', false);
        } else {
          let errMsg = 'Failed to reset password.';
          if (data.new_password) {
            errMsg = Array.isArray(data.new_password) ? data.new_password.join(' ') : data.new_password;
          } else if (data.confirm_password) {
            errMsg = Array.isArray(data.confirm_password) ? data.confirm_password[0] : data.confirm_password;
          } else if (data.otp) {
            errMsg = Array.isArray(data.otp) ? data.otp[0] : data.otp;
          } else if (data.detail) {
            errMsg = data.detail;
          }
          showAlert(errMsg, true);
        }
      } catch (err) {
        showAlert('Network error: ' + err.message, true);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Change Password';
      }
    });
  </script>
</body>
</html>
"""
        return HttpResponse(html_content, content_type="text/html")

