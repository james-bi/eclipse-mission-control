from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Balloon, BalloonImage, TelemetryData

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

        balloon, created = Balloon.objects.get_or_create(
            balloon_id=balloon_id,
            defaults={'name': balloon_id, 'status': 'active'}
        )

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
            
        balloon, created = Balloon.objects.get_or_create(
            balloon_id=balloon_id,
            defaults={'name': balloon_id, 'status': 'active'}
        )
            
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

def balloon_telemetry_api(request, balloon_id):
    balloon = get_object_or_404(Balloon, balloon_id=balloon_id)

    max_points = 500
    total_telemetry = balloon.telemetry.count()
    skip_points = max(0, total_telemetry - max_points)
    telemetry_qs = balloon.telemetry.order_by('timestamp').values('timestamp', 'altitude', 'latitude', 'longitude', 'temperature')
    telemetry_data = list(telemetry_qs[skip_points:])

    ascent_rate = 0
    if len(telemetry_data) >= 2:
        recent = telemetry_data[-2:]
        time_diff = (recent[1]['timestamp'] - recent[0]['timestamp']).total_seconds()
        alt_diff = recent[1]['altitude'] - recent[0]['altitude']
        if time_diff > 0:
            ascent_rate = alt_diff / time_diff

    latest_telemetry = balloon.telemetry.order_by('-timestamp').first()

    return JsonResponse({
        'balloon_id': balloon.balloon_id,
        'latest_telemetry': {
            'latitude': round(latest_telemetry.latitude, 4) if latest_telemetry else 'N/A',
            'longitude': round(latest_telemetry.longitude, 4) if latest_telemetry else 'N/A',
            'altitude': round(latest_telemetry.altitude, 0) if latest_telemetry else 'N/A',
            'temperature': round(latest_telemetry.temperature, 1) if latest_telemetry else 'N/A',
            'timestamp': latest_telemetry.timestamp.isoformat() if latest_telemetry else None,
        },
        'ascent_rate': round(ascent_rate, 2),
        'telemetry_data': [{
            'timestamp': point['timestamp'].isoformat(),
            'altitude': point['altitude'],
            'latitude': point['latitude'],
            'longitude': point['longitude'],
            'temperature': point['temperature'],
        } for point in telemetry_data]
    })


def balloon_detail(request, balloon_id):
    balloon = get_object_or_404(Balloon, balloon_id=balloon_id)
    
    # Get latest telemetry
    latest_telemetry = balloon.telemetry.order_by('-timestamp').first()
    
    # Limit telemetry data to last 500 points to prevent memory overload
    max_points = 500
    total_telemetry = balloon.telemetry.count()
    skip_points = max(0, total_telemetry - max_points)

    telemetry_qs = balloon.telemetry.order_by('timestamp').values('timestamp', 'altitude', 'latitude', 'longitude', 'temperature')
    raw_points = list(telemetry_qs[skip_points:])
    telemetry_data = []
    for point in raw_points:
        telemetry_data.append({
            'timestamp': point['timestamp'].isoformat(),
            'altitude': float(point['altitude']),
            'latitude': float(point['latitude']),
            'longitude': float(point['longitude']),
            'temperature': float(point['temperature']),
        })

    # Calculate ascent rate (m/s) from last two points
    ascent_rate = 0
    if len(raw_points) >= 2:
        recent = raw_points[-2:]
        time_diff = (recent[1]['timestamp'] - recent[0]['timestamp']).total_seconds()
        alt_diff = float(recent[1]['altitude']) - float(recent[0]['altitude'])
        if time_diff > 0:
            ascent_rate = alt_diff / time_diff
    
    context = {
        'balloon': balloon,
        'latest_telemetry': latest_telemetry,
        'telemetry_data': json.dumps(telemetry_data),
        'ascent_rate': round(ascent_rate, 2),
        'google_maps_api_key': 'AIzaSyCKkt3WQ48-xNJPOhruaIaxV6-GB35XEgE',  # Replace with actual key
    }
    
    return render(request, 'telemetry/balloon_detail.html', context)
