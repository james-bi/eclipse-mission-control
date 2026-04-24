from django.db import models

class Balloon(models.Model):
    name = models.CharField(max_length=100)
    balloon_id = models.SlugField(unique=True)  # e.g., 'eagle-1'
    is_active = models.BooleanField(default=True)

    def __cl__(self):
        return self.name

class Telemetry(models.Model):
    balloon = models.ForeignKey(Balloon, on_delete=models.CASCADE, related_name='telemetry')
    timestamp = models.DateTimeField(auto_now_add=True)
    altitude = models.FloatField()  # In meters
    temperature = models.FloatField()  # In Celsius
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ['-timestamp']

class MissionPhoto(models.Model):
    balloon = models.ForeignKey(Balloon, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(max_length=500)  # The S3 link sent by the Pi
    timestamp = models.DateTimeField(auto_now_add=True)