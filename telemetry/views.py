from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Balloon, BalloonImage

def dashboard_view(request):
    balloons = Balloon.objects.all()
    return render(request, 'dashboard.html', {'balloons': balloons})

@csrf_exempt
@require_POST
def receive_image_metadata(request):
    try:
        data = json.loads(request.body)
        balloon_id = data.get('balloon_id')
        image_url = data.get('url')

        if not balloon_id or not image_url:
            return JsonResponse({'error': 'Missing balloon_id or url'}, status=400)

        try:
            balloon = Balloon.objects.get(balloon_id=balloon_id)
        except Balloon.DoesNotExist:
            return JsonResponse({'error': 'Balloon not found'}, status=404)

        image = BalloonImage.objects.create(balloon=balloon, image_url=image_url)
        
        return JsonResponse({
            'message': 'Image metadata saved successfully',
            'image_id': image.id
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def receive_telemetry(request):
    try:
        data = json.loads(request.body)
        balloon_id = data.get('balloon_id')
        
        if not balloon_id:
            return JsonResponse({'error': 'Missing balloon_id'}, status=400)
            
        try:
            balloon = Balloon.objects.get(balloon_id=balloon_id)
        except Balloon.DoesNotExist:
            return JsonResponse({'error': 'Balloon not found'}, status=404)
            
        # Create telemetry data
        TelemetryData.objects.create(
            balloon=balloon,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            altitude=data.get('altitude'),
            temperature=data.get('temperature'),
            battery_level=data.get('battery_level')
        )
        
        return JsonResponse({'message': 'Telemetry data saved successfully'}, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def latest_telemetry(request):
    balloons = Balloon.objects.all()
    data = []
    
    for balloon in balloons:
        latest = balloon.telemetry.order_by('-timestamp').first()
        
        display_status = 'Active' if balloon.status in ['IN_FLIGHT', 'active'] else 'Lost'
        is_active = (display_status == 'Active')
        
        if latest:
            data.append({
                'balloon_id': balloon.balloon_id,
                'name': balloon.name,
                'status': display_status,
                'is_active': is_active,
                'timestamp': latest.timestamp.isoformat(),
                'latitude': round(latest.latitude, 4),
                'longitude': round(latest.longitude, 4),
                'altitude': round(latest.altitude, 2),
                'temperature': round(latest.temperature, 2),
                'battery_level': round(latest.battery_level, 2),
            })
        else:
            data.append({
                'balloon_id': balloon.balloon_id,
                'name': balloon.name,
                'status': display_status,
                'is_active': is_active,
                'timestamp': None,
                'latitude': 'N/A',
                'longitude': 'N/A',
                'altitude': 'N/A',
                'temperature': 'N/A',
                'battery_level': 'N/A',
            })
            
    return JsonResponse({'telemetry': data})

def get_balloon_image(request, balloon_id):
    from django.shortcuts import get_object_or_404
    balloon = get_object_or_404(Balloon, balloon_id=balloon_id)
    
    current_id = request.GET.get('current_id', request.GET.get('current_image_id'))
    direction = request.GET.get('dir', request.GET.get('action'))
    
    image = None
    if current_id:
        try:
            current_image = BalloonImage.objects.get(id=current_id)
            if direction == 'next':
                image = balloon.images.filter(timestamp__lt=current_image.timestamp).order_by('-timestamp').first()
                if not image:
                    image = balloon.images.order_by('-timestamp').first()
            elif direction in ['prev', 'back']:
                image = balloon.images.filter(timestamp__gt=current_image.timestamp).order_by('timestamp').first()
                if not image:
                    image = balloon.images.order_by('timestamp').first()
        except BalloonImage.DoesNotExist:
            pass

    if not image:
        image = balloon.images.order_by('-timestamp').first()

    return render(request, 'telemetry/partials/image_carousel.html', {
        'balloon': balloon,
        'image': image
    })
