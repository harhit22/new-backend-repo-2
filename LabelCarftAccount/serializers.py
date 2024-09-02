from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def create(self, validated_data):
        password1 = validated_data.pop('password1')
        password2 = validated_data.pop('password2')

        if password1 != password2:
            raise serializers.ValidationError('password dont match')

        email = validated_data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        user = User.objects.create_user(**validated_data, password=password1)
        user.is_active = True
        user.save()

        return user


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, min_length=4, write_only=True)
    email = serializers.CharField(max_length=255, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']