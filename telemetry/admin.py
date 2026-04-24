from django.contrib import admin
from .models import Balloon, TelemetryData, BalloonImage

@admin.register(Balloon)
class BalloonAdmin(admin.ModelAdmin):
    list_display = ('name', 'balloon_id', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'balloon_id')

@admin.register(TelemetryData)
class TelemetryDataAdmin(admin.ModelAdmin):
    list_display = ('balloon', 'timestamp', 'latitude', 'longitude', 'altitude', 'temperature', 'battery_level')
    list_filter = ('balloon', 'timestamp')
    search_fields = ('balloon__name', 'balloon__balloon_id')
    readonly_fields = ('timestamp',)

@admin.register(BalloonImage)
class BalloonImageAdmin(admin.ModelAdmin):
    list_display = ('balloon', 'timestamp', 'image_url')
    list_filter = ('balloon', 'timestamp')
    search_fields = ('balloon__name', 'balloon__balloon_id', 'image_url')
    readonly_fields = ('timestamp',)
