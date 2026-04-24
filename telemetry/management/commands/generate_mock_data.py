import random
from django.core.management.base import BaseCommand
from telemetry.models import Balloon, TelemetryData

class Command(BaseCommand):
    help = 'Generates 8 mock balloons and random telemetry data points for each'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating mock data...")

        balloons = []
        for i in range(1, 9):
            balloon, created = Balloon.objects.get_or_create(
                balloon_id=f"B00{i}",
                defaults={'name': f"High-Altitude Balloon {i}", 'status': 'IN_FLIGHT'}
            )
            balloons.append(balloon)
            if created:
                self.stdout.write(f"Created {balloon.name}")

        for balloon in balloons:
            # Generate 5 mock points per balloon
            for _ in range(5):
                lat = random.uniform(30.0, 45.0) # roughly US latitudes
                lon = random.uniform(-120.0, -75.0) # roughly US longitudes
                alt = random.uniform(10000, 30000) # 10k to 30k meters
                temp = random.uniform(-60.0, 10.0) # cold at high altitude
                battery = random.uniform(10.0, 100.0)
                
                TelemetryData.objects.create(
                    balloon=balloon,
                    latitude=lat,
                    longitude=lon,
                    altitude=alt,
                    temperature=temp,
                    battery_level=battery
                )
            self.stdout.write(f"Generated telemetry points for {balloon.name}")
        
        self.stdout.write(self.style.SUCCESS("Successfully generated mock data!"))
