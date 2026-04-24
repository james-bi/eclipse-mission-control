from django.shortcuts import render
from django.http import HttpResponse
from .models import Balloon, Telemetry

def dashboard_home(request):
    balloons = Balloon.objects.all()
    context = {
        'balloons': balloons
    }
    return render(request, 'dashboard/index.html', context)

def telemetry_partial(request):
    # Fetch the first active balloon
    balloon = Balloon.objects.filter(is_active=True).first()
    if balloon:
        # Get the latest telemetry for this balloon
        latest_telemetry = Telemetry.objects.filter(balloon=balloon).order_by('-timestamp').first()
        if latest_telemetry:
            html = f"""
            <div class="text-lg">
                <p><span class="font-semibold text-slate-500">Balloon:</span> {balloon.name}</p>
                <p><span class="font-semibold text-slate-500">Altitude:</span> {latest_telemetry.altitude} m</p>
                <p><span class="font-semibold text-slate-500">Temperature:</span> {latest_telemetry.temperature} &deg;C</p>
            </div>
            """
            return HttpResponse(html)
        else:
            return HttpResponse('<p class="text-slate-400">No telemetry data for active balloon.</p>')
    else:
        return HttpResponse('<p class="text-slate-400">No active balloons found.</p>')
