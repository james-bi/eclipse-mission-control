# Weather Balloon Telemetry API Documentation

## Overview

This Django-based mission control dashboard receives telemetry data from weather balloons for a scout camp project. Balloons can send real-time data including position, altitude, temperature, battery level, and photographs.

## API Endpoints

### 1. Send Telemetry Data
**Endpoint:** `POST /api/telemetry/receive/`  
**Content-Type:** `application/json`  
**CSRF Exempt:** Yes (designed for external device communication)

#### Request Body
```json
{
  "balloon_id": "string",  // Required: Unique identifier for the balloon (e.g., "scout-1")
  "latitude": number,      // Required: Latitude in decimal degrees
  "longitude": number,     // Required: Longitude in decimal degrees
  "altitude": number,      // Required: Altitude in meters
  "temperature": number,   // Required: Temperature in Celsius
  "battery_level": number  // Required: Battery level as percentage (0-100)
}
```

#### Response
**Success (201):**
```json
{
  "message": "Telemetry data saved successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields or invalid JSON
- `404 Not Found`: Balloon with specified ID doesn't exist
- `500 Internal Server Error`: Server error

#### Example Request
```bash
curl -X POST http://your-server.com/api/telemetry/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "balloon_id": "scout-1",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 15000.5,
    "temperature": -25.3,
    "battery_level": 85.7
  }'
```

### 2. Send Image Metadata
**Endpoint:** `POST /api/image/receive/`  
**Content-Type:** `application/json`  
**CSRF Exempt:** Yes

#### Request Body
```json
{
  "balloon_id": "string",  // Required: Unique identifier for the balloon
  "url": "string"          // Required: URL to the image (e.g., S3 bucket URL)
}
```

#### Response
**Success (201):**
```json
{
  "message": "Image metadata saved successfully",
  "image_id": 123
}
```

**Error Responses:**
- `400 Bad Request`: Missing balloon_id or url
- `404 Not Found`: Balloon not found
- `500 Internal Server Error`: Server error

#### Example Request
```bash
curl -X POST http://your-server.com/api/image/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "balloon_id": "scout-1",
    "url": "https://s3.amazonaws.com/your-bucket/balloon-image-001.jpg"
  }'
```

### 3. Get Latest Telemetry (Dashboard)
**Endpoint:** `GET /api/telemetry/`  
**Response:** JSON array of all balloons with their latest telemetry data

## Balloon Setup

### 1. Register Balloons
Balloons must be registered in the system before sending data. This is typically done through the Django admin interface at `/admin/`.

Required fields:
- **Name**: Human-readable name (e.g., "Scout Troop 123 Balloon")
- **Balloon ID**: Unique slug identifier (e.g., "scout-123")
- **Status**: Active/Lost/Landed

### 2. Data Transmission
Balloons should transmit data periodically (e.g., every 30-60 seconds) using HTTP POST requests to the appropriate endpoints.

## Testing and Development

### Mock Data Generation
Generate test balloons and telemetry data:
```bash
python manage.py generate_mock_data
```

### Flight Simulation
Continuously simulate balloon flight with realistic telemetry:
```bash
python manage.py simulate_flight --interval 5
```
This creates new telemetry points every 5 seconds for all balloons.

## Data Models

### Balloon
- `name`: CharField (display name)
- `balloon_id`: SlugField (unique identifier)
- `status`: ChoiceField (active/lost/landed)

### TelemetryData
- `balloon`: ForeignKey to Balloon
- `timestamp`: DateTimeField (auto-generated)
- `latitude`: DecimalField (9 digits, 6 decimal places)
- `longitude`: DecimalField (9 digits, 6 decimal places)
- `altitude`: FloatField (meters)
- `temperature`: FloatField (Celsius)
- `battery_level`: IntegerField (percentage)

### BalloonImage
- `balloon`: ForeignKey to Balloon
- `timestamp`: DateTimeField (auto-generated)
- `image_url`: URLField (link to image)

## Implementation Notes

### For Balloon Hardware
1. **GPS Module**: Required for latitude/longitude
2. **Altimeter/Barometer**: For altitude and pressure data
3. **Temperature Sensor**: Ambient temperature
4. **Battery Monitor**: Voltage/current sensing
5. **Camera**: For periodic photographs
6. **Cellular/LoRa/Radio Module**: For data transmission

### Data Transmission Strategy
- Use HTTP POST with JSON payloads
- Implement retry logic for failed transmissions
- Consider data compression for bandwidth-limited connections
- Include timestamp in payload if device clock is reliable

### Security Considerations
- Endpoints are CSRF-exempt for external access
- Consider adding API key authentication for production
- Validate data ranges (e.g., reasonable lat/lon values)
- Monitor for unusual data patterns

## Troubleshooting

### Common Issues
1. **"Balloon not found"**: Ensure balloon_id matches exactly what's registered
2. **Connection timeouts**: Check server URL and network connectivity
3. **Invalid JSON**: Verify payload format and required fields

### Monitoring
- Check Django admin for received data
- Monitor server logs for errors
- Use the dashboard at `/` to view real-time telemetry</content>
<parameter name="filePath">/workspaces/eclipse-mission-control/API_DOCUMENTATION.md