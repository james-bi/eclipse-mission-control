from django.shortcuts import render
from .models import Balloon

def dashboard_home(request):
    balloons = Balloon.objects.all()
    context = {
        'balloons': balloons
    }
    return render(request, 'dashboard/index.html', context)
