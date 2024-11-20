from .email_verification import send_verification_email  # Correct import statement
from .token import user_tokenizer_generate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework import views, permissions, status
from .backend import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .password_reset import send_password_reset_email

class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.perform_create(serializer)
            send_verification_email(user, request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return serializer.save()


class EmailVerificationView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print(user)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        print(user_tokenizer_generate.check_token(user, token))
        if user and user_tokenizer_generate.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('email_verification_success')
        else:
            return


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate the JWT token
        jwt_token = JWTAuthentication.create_jwt(user)

        return Response({'token': jwt_token, "username": user.username, 'user_id': user.id, 'email': user.email})


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Instantiate JWTAuthentication to access the invalidate_token method
        jwt_auth = JWTAuthentication()
        jwt_auth.invalidate_token(request)

        return Response({"detail": "Successfully logged out."})



class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        token = user_tokenizer_generate.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"http://34.68.171.158/reset-password/{uid}/{token}/"
        send_password_reset_email(user, reset_url)

        return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)



class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and user_tokenizer_generate.check_token(user, token):
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
