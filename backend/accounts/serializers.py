from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'full_name', 'username', 'email', 'password', 'confirm_password')

    def validate(self, attrs):
        full_name = attrs.get('full_name', '').strip()
        username = attrs.get('username', '').strip()
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if not full_name:
            raise serializers.ValidationError({"full_name": "Full name is required."})
        if not username:
            raise serializers.ValidationError({"username": "Username is required."})
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(
            username=validated_data['username'].strip(),
            email=validated_data['email'].strip().lower(),
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '').strip(),
            role=User.Role.USER
        )
        return user

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        identifier = attrs.get('username_or_email', '').strip()
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Both username/email and password are required.")

        user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials. Please check your username/email and password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        refresh = RefreshToken.for_user(user)
        # Custom claims in JWT
        refresh['role'] = user.role
        refresh['username'] = user.username
        refresh['email'] = user.email

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_admin': user.is_admin,
            }
        }

class UserSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'is_staff', 'date_joined', 'orders_count')
        read_only_fields = ('id', 'role', 'is_staff', 'date_joined')

    def get_orders_count(self, obj):
        return obj.orders.count()

class UserProfileSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False, min_length=6, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'new_password')
        read_only_fields = ('id', 'username', 'role')

    def validate_email(self, value):
        user = self.instance
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already in use by another user.")
        return normalized

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        instance.full_name = validated_data.get('full_name', instance.full_name).strip()
        instance.email = validated_data.get('email', instance.email).strip().lower()

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance
