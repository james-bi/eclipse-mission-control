from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.conf import settings
import json
import logging
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from .models import Balloon, BalloonImage, TelemetryData

logger = logging.getLogger(__name__)

# Global storage for logs (no database)
logs_by_balloon = {}

def sanitize_balloon_id(balloon_id):
    """
    Convert any string to a valid SlugField value.
    Replaces spaces and special characters with hyphens.
    """
    if not balloon_id:
        return None
    return slugify(balloon_id)

def get_s3_signed_url(s3_url, expiration=3600):
    """
    Generate a signed URL for S3 objects if AWS credentials are configured.
    Returns the original URL if not an S3 URL or credentials not available.
    """
    if not s3_url or not s3_url.startswith('https://') or 's3' not in s3_url:
        return s3_url
    
    # Check if AWS credentials are configured
    if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_REGION]):
        return s3_url
    
    try:
        # Parse S3 URL to extract bucket and key
        # URL format: https://bucket-name.s3.region.amazonaws.com/key
        # or https://s3.region.amazonaws.com/bucket-name/key
        if '.s3.' in s3_url:
            # https://bucket-name.s3.region.amazonaws.com/key
            parts = s3_url.replace('https://', '').split('.s3.')
            if len(parts) == 2:
                bucket = parts[0]
                region_and_key = parts[1].split('/', 1)
                if len(region_and_key) == 2:
                    region = region_and_key[0].split('.')[0]  # Extract region from region.amazonaws.com
                    key = region_and_key[1]
                else:
                    return s3_url
            else:
                return s3_url
        elif 's3.' in s3_url:
            # https://s3.region.amazonaws.com/bucket-name/key
            parts = s3_url.replace('https://', '').split('/', 2)
            if len(parts) >= 3:
                region = parts[0].replace('s3.', '').replace('.amazonaws.com', '')
                bucket = parts[1]
                key = parts[2]
            else:
                return s3_url
        else:
            return s3_url
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Generate signed URL
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        
        return signed_url
        
    except (NoCredentialsError, Exception) as e:
        # If signing fails, return original URL
        return s3_url

@login_required
def dashboard_view(request):
    balloons = Balloon.objects.all()
    return render(request, 'dashboard.html', {'balloons': balloons})

@csrf_exempt
@require_POST
def receive_image_metadata(request):
    try:
        data = json.loads(request.body)
        balloon_id = data.get('balloon_id')
        image_url = data.get('url') or data.get('s3_url') or data.get('photo_url') or data.get('image_url')

        if not balloon_id or not image_url:
            return JsonResponse({'error': 'Missing balloon_id or url'}, status=400)

        balloon, created = Balloon.objects.get_or_create(
            balloon_id=balloon_id,
            defaults={'name': balloon_id, 'status': 'active'}
        )

        filename = data.get('filename') or image_url.split('/')[-1] if image_url else None

        image = BalloonImage.objects.create(balloon=balloon, image_url=image_url, filename=filename)
        
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
def receive_photo_notification(request):
    """
    Receive photo notifications from balloons.
    Supports JSON and form-encoded payloads.
    """
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
        
        # Extract image URL
        image_url = data.get('s3_url') or data.get('url') or data.get('photo_url') or data.get('image_url')
        balloon_id = data.get('balloon_id') or data.get('device_id') or data.get('id')
        
        if not balloon_id or not image_url:
            return JsonResponse({'error': 'Missing balloon_id or url'}, status=400)
        
        # Extract or derive balloon_id
        if not balloon_id:
            # Derive from S3 path if available
            try:
                # Extract directory name from S3 URL as fallback balloon_id
                parts = image_url.split('/')
                if len(parts) > 1:
                    balloon_id = sanitize_balloon_id(parts[-2]) or 'scout-1'
                else:
                    balloon_id = 'scout-1'
            except Exception:
                balloon_id = 'scout-1'
        
        balloon_id = sanitize_balloon_id(balloon_id)
        if not balloon_id:
            balloon_id = 'scout-1'

        balloon, created = Balloon.objects.get_or_create(
            balloon_id=balloon_id,
            defaults={'name': balloon_id, 'status': 'active'}
        )

        filename = data.get('filename') or image_url.split('/')[-1] if image_url else None

        image = BalloonImage.objects.create(balloon=balloon, image_url=image_url, filename=filename)
        
        return JsonResponse({
            'message': 'Photo notification received and saved successfully',
            'image_id': image.id
        }, status=201)
    except Exception as e:
        logger.exception('Failed to process photo notification')
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def receive_logs(request):
    try:
        data = json.loads(request.body)
        balloon_id = data.get('balloon_id')
        if not balloon_id:
            return JsonResponse({'error': 'Missing balloon_id'}, status=400)
        
        new_logs = data.get('logs', [])
        
        # Append new logs to existing logs for this balloon
        if balloon_id not in logs_by_balloon:
            logs_by_balloon[balloon_id] = []
        
        logs_by_balloon[balloon_id].extend(new_logs)
        
        # Keep only last 500 logs per balloon to prevent unbounded memory growth
        if len(logs_by_balloon[balloon_id]) > 500:
            logs_by_balloon[balloon_id] = logs_by_balloon[balloon_id][-500:]
        
        return JsonResponse({'message': 'Logs received successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_balloon_logs(request, balloon_id):
    logs = logs_by_balloon.get(balloon_id, [])
    html = ''
    
    if logs:
        for log in logs:  # Show all accumulated logs
            try:
                timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%H:%M:%S.%f')[:-3]
            except (ValueError, TypeError):
                timestamp = '??:??:??.???'
            level = log.get('level', 'INFO').upper()
            message = log.get('message', '')
            # Escape HTML characters for safety
            message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += f'<div>[{timestamp}] <span class="text-yellow-300">{level}</span>: {message}</div>'
    else:
        html = '<div class="text-gray-500">Waiting for logs...</div>'
    
    return HttpResponse(html)

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
            battery_level=data.get('battery_level'),
            flight_phase=data.get('flight_phase')
        )
        
        return JsonResponse({'message': 'Telemetry data saved successfully'}, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
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

@login_required
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

    # Generate signed URL if it's an S3 URL
    if image:
        image.image_url = get_s3_signed_url(image.image_url)

    return render(request, 'telemetry/partials/image_carousel.html', {
        'balloon': balloon,
        'image': image
    })

@login_required
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
            'flight_phase': latest_telemetry.flight_phase if latest_telemetry else 'N/A',
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


@login_required
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
        'logs': logs_by_balloon.get(balloon_id, []),
    }
    
    return render(request, 'telemetry/balloon_detail.html', context)
