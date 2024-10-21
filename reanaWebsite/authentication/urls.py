from django.urls import path
from .views import RegistrationView, UsernameValidationView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"),
    path('username_validation', csrf_exempt(UsernameValidationView.as_view()), name='username_validation')
]