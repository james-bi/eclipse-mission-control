import time
import random
from django.core.management.base import BaseCommand
from telemetry.models import Balloon, TelemetryData

class Command(BaseCommand):
    help = 'Simulates a flight by continuously generating telemetry data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Interval in seconds between simulation steps'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(self.style.SUCCESS(f"Starting flight simulation with {interval}s interval... Press Ctrl+C to stop."))
        initial_pass = True
        
        try:
            while True:
                balloons = Balloon.objects.filter(status__in=['active', 'IN_FLIGHT'])
                if not balloons.exists():
                    balloons = Balloon.objects.all()
                
                for balloon in balloons:
                    latest = balloon.telemetry.order_by('-timestamp').first()
                    
                    if latest and not initial_pass:
                        # Continue from last known telemetry
                        lat = float(latest.latitude) + random.uniform(-0.01, 0.01)
                        lon = float(latest.longitude) + random.uniform(-0.01, 0.01)
                        
                        # Go up
                        alt = latest.altitude + random.uniform(50, 300)
                        if alt > 35000:
                            alt = random.uniform(34000, 35000)
                            
                        # Temperature decreases as altitude increases, roughly 6.5C per 1000m up to tropopause
                        temp = max(-60.0, float(latest.temperature) - random.uniform(0.1, 1.0))
                        
                        # Battery drains
                        battery = max(0.0, float(latest.battery_level) - random.uniform(0.05, 0.5))
                    else:
                        # Start from ground for this simulation run
                        lat = random.uniform(30.0, 45.0)
                        lon = random.uniform(-120.0, -75.0)
                        alt = random.uniform(100, 500)
                        temp = random.uniform(15.0, 25.0)
                        battery = 100.0
                        
                    TelemetryData.objects.create(
                        balloon=balloon,
                        latitude=lat,
                        longitude=lon,
                        altitude=alt,
                        temperature=temp,
                        battery_level=battery
                    )
                
                initial_pass = False
                self.stdout.write(f"Generated new telemetry for {balloons.count()} balloons.")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nSimulation stopped by user.'))
