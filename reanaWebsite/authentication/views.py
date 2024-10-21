from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import View
from django.contrib import messages
import json
from django.http import HttpResponse, JsonResponse
from validate_email import validate_email
from django.contrib import auth


# Create your views here.
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = True
        user.save()

        return render(request, 'authentication/login.html', context)
    
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html', {
            'username': 'Enter your username',
            'password': 'Enter your password'
        })
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('index')
            return render(request, 'authentication/login.html', {
                'username': username,
                'password': 'Invalid username or password'
            })
        return render(request, 'authentication/login.html', {
            'username': username if username else 'Please fill all fields',
            'password': 'Please fill all fields'
        })
    
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})
    
class PasswordValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        password = data['password']
        if len(str(password)) < 8:
            return JsonResponse({'password_error': 'Password must be at least 8 characters long.'}, status=400)
        return JsonResponse({'password_valid': True})
    
# 409 : conflix
# 400 : bad request
# 401 : unauthorized
# 403 : forbidden
# 404 : not found
# 500 : internal server error