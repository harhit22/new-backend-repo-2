from django.urls import path
from . import views

urlpatterns = [
    path("api/register", views.UserRegistrationAPIView.as_view(), name='api-register'),
    path('api/email-varification/<str:uidb64>/<str:token>', views.EmailVerificationView.as_view(), name='api-emai-verification'),

    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('send-reset-email/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
