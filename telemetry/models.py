from django.db import models

class Balloon(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('lost', 'Lost'),
        ('landed', 'Landed'),
    ]
    name = models.CharField(max_length=100)
    balloon_id = models.SlugField(unique=True) # e.g., 'scout-1'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.name} ({self.balloon_id})"

class TelemetryData(models.Model):
    balloon = models.ForeignKey(Balloon, on_delete=models.CASCADE, related_name='telemetry')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.FloatField() # In meters
    temperature = models.FloatField() # In Celsius
    battery_level = models.IntegerField() # Percentage

    class Meta:
        ordering = ['-timestamp']

class BalloonImage(models.Model):
    balloon = models.ForeignKey(Balloon, on_delete=models.CASCADE, related_name='images')
    timestamp = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(max_length=500) # The S3 Link

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Image from {self.balloon.name} at {self.timestamp}"