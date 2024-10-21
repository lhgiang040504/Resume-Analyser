from django.urls import path
from .views import RegistrationView, UsernameValidationView, EmailValidationView, LoginView, PasswordValidationView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('username_validation', csrf_exempt(UsernameValidationView.as_view()), name='username_validation'),
    path('email_validation', csrf_exempt(EmailValidationView.as_view()), name='email_validation'),
    path('password_validation', csrf_exempt(PasswordValidationView.as_view()), name='password_validation'),
]