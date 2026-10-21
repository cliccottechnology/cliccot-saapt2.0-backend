from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, PasswordResetOTP

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'confirm_password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_email(self, value):
        normalized_email = value.lower()
        if CustomUser.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Password fields do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Supports login with either username or email.
    """
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        identifier = data.get('username_or_email')
        password = data.get('password')

        # Check if identifier matches an email or username
        user_obj = None
        if '@' in identifier:
            user_obj = CustomUser.objects.filter(email__iexact=identifier).first()
        else:
            user_obj = CustomUser.objects.filter(username=identifier).first()

        if user_obj is None:
            raise serializers.ValidationError({"detail": "Invalid credentials. User does not exist."})

        # Authenticate using the actual username
        user = authenticate(username=user_obj.username, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "Invalid username/email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "This account is inactive."})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class LoginUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data returned upon login.
    """
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'phone_number',
        )
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating current user profile.
    """
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'username', 'email', 'created_at', 'updated_at')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_new_password'):
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})
        return attrs


class ForgotPasswordRequestSerializer(serializers.Serializer):
    """
    Serializer to request a password reset OTP by providing email.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        user = CustomUser.objects.filter(email__iexact=normalized_email).first()
        if not user:
            raise serializers.ValidationError("No account found with this email address.")
        if not user.is_active:
            raise serializers.ValidationError("This account is currently inactive.")
        self.user = user
        return normalized_email


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer to verify the OTP sent to user's email.
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email').lower().strip()
        otp = attrs.get('otp').strip()

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError({"email": "No account found with this email address."})

        # Fetch latest active OTP for this user
        otp_record = PasswordResetOTP.objects.filter(
            user=user,
            email=email,
            is_used=False
        ).order_by('-created_at').first()

        if not otp_record:
            raise serializers.ValidationError({"otp": "No active OTP request found. Please request a new OTP."})

        if otp_record.is_expired:
            raise serializers.ValidationError({"otp": "OTP has expired. Please request a new OTP."})

        if otp_record.otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP. Please check the code sent to your email."})

        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer to reset user password after OTP verification.
    Accepts either 'otp' or 'reset_token', along with new password and confirmation.
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=False, allow_blank=True, max_length=6)
    reset_token = serializers.CharField(required=False, allow_blank=True, max_length=64)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_new_password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email').lower().strip()
        otp = (attrs.get('otp') or '').strip()
        reset_token = (attrs.get('reset_token') or '').strip()
        new_password = attrs.get('new_password')
        confirm_pass = attrs.get('confirm_password') or attrs.get('confirm_new_password')

        if not confirm_pass:
            raise serializers.ValidationError({"confirm_password": "Confirm password is required."})

        if new_password != confirm_pass:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})

        if not otp and not reset_token:
            raise serializers.ValidationError({"detail": "Either 'otp' or 'reset_token' is required to reset password."})

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError({"email": "No account found with this email address."})

        # Match by reset_token or otp
        query = PasswordResetOTP.objects.filter(user=user, is_used=False)
        if reset_token:
            otp_record = query.filter(reset_token=reset_token).first()
        else:
            otp_record = query.filter(otp=otp).order_by('-created_at').first()

        if not otp_record:
            raise serializers.ValidationError({"otp": "Invalid or expired OTP/reset token. Please request a new OTP."})

        if otp_record.is_expired:
            raise serializers.ValidationError({"otp": "OTP/reset token has expired. Please request a new OTP."})

        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs

