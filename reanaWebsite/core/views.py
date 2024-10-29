from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm

# Create your views here.
@login_required(login_url='/authentication/login')
def index(request):
    return render(request, 'core/index.html')

@login_required(login_url='/authentication/login')
def news(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
    else:
        form = UploadFileForm()
    # Access the user's name from the context
    username = request.user.username

    context = {
        'username': username,
        'form': form,
    }

    # Render the news template with the username
    return render(request, 'core/news.html', context)
