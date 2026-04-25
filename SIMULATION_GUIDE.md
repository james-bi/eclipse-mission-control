# Balloon Simulation and Testing Guide

This guide covers how to set up, simulate, and test your Eclipse Mission Control balloon tracking system.

## Prerequisites

- Python 3.10+
- MySQL database
- Git

## Setup

### 1. Clone and Install
```bash
git clone https://github.com/your-username/eclipse-mission-control.git
cd eclipse-mission-control
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE eclipse_mission_control;
GRANT ALL PRIVILEGES ON eclipse_mission_control.* TO 'eclipse_user'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://eclipse_user:your_password@localhost:3306/eclipse_mission_control
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## Creating Balloons

### Via Django Admin
1. Start the server: `python manage.py runserver`
2. Visit `http://localhost:8000/admin/`
3. Login with superuser credentials
4. Go to "Telemetry > Balloons" and click "Add Balloon"
5. Fill in:
   - **Name**: "Scout Troop 123 Balloon"
   - **Balloon ID**: "scout-123" (unique identifier)
   - **Status**: "active"

### Via Management Command
```bash
# Generate 8 sample balloons with mock data
python manage.py generate_mock_data
```

## Simulation Commands

### Simulate All Balloons
```bash
# Basic simulation (5 second intervals)
python manage.py simulate_flight

# Custom interval (10 seconds)
python manage.py simulate_flight --interval 10
```

### Simulate Specific Balloon
```bash
# Target balloon by ID
python manage.py simulate_flight --balloon-id B001

# Target with custom interval
python manage.py simulate_flight --balloon-id scout-123 --interval 3
```

### Simulation Behavior
- **First run**: Starts from ground level (~100-500m altitude)
- **Subsequent runs**: Continues from last known position
- **Realistic physics**: Altitude increases, temperature decreases, battery drains
- **Geographic movement**: Slight position changes to simulate wind
- **Safety limits**: Altitude caps at ~35,000m, temperature minimum -60°C

## Testing the API

### Start Development Server
```bash
python manage.py runserver
```

### Manual API Testing

#### Send Telemetry Data
```bash
curl -X POST http://localhost:8000/api/telemetry/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "balloon_id": "B001",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 15000,
    "temperature": -25.3,
    "battery_level": 85.7
  }'
```

#### Send Image Data
```bash
curl -X POST http://localhost:8000/api/image/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "balloon_id": "B001",
    "url": "https://example.com/balloon-image.jpg"
  }'
```

### View Dashboards

#### Main Fleet Dashboard
- URL: `http://localhost:8000/`
- Shows all balloons with status and "View Dashboard" buttons

#### Individual Balloon Dashboard
- URL: `http://localhost:8000/balloon/<balloon_id>/`
- Example: `http://localhost:8000/balloon/B001/`
- Features:
  - Real-time telemetry stats
  - Interactive Google Maps with flight path
  - Altitude and temperature charts
  - Image carousel

#### API Endpoints
- Latest telemetry: `http://localhost:8000/api/telemetry/`
- Admin interface: `http://localhost:8000/admin/`

## Simulation Scenarios

### Scenario 1: Single Balloon Test
```bash
# Create one balloon
python manage.py shell -c "
from telemetry.models import Balloon
Balloon.objects.create(name='Test Balloon', balloon_id='test-1', status='active')
"

# Simulate it
python manage.py simulate_flight --balloon-id test-1 --interval 2

# View dashboard in browser: http://localhost:8000/balloon/test-1/
```

### Scenario 2: Multiple Balloon Race
```bash
# Generate multiple balloons
python manage.py generate_mock_data

# Simulate all balloons
python manage.py simulate_flight --interval 5

# View main dashboard: http://localhost:8000/
```

### Scenario 3: API Integration Test
```bash
# Terminal 1: Start server
python manage.py runserver

# Terminal 2: Simulate balloon
python manage.py simulate_flight --balloon-id B001

# Terminal 3: Send manual telemetry
curl -X POST http://localhost:8000/api/telemetry/receive/ \
  -H "Content-Type: application/json" \
  -d '{"balloon_id": "B001", "latitude": 35.0, "longitude": -80.0, "altitude": 20000, "temperature": -30, "battery_level": 90}'
```

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL service
sudo systemctl status mysql

# Test database connection
python manage.py dbshell
```

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Apply missing migrations
python manage.py migrate
```

### Balloon Not Found Errors
- Ensure balloon exists: `python manage.py shell -c "from telemetry.models import Balloon; print(Balloon.objects.all())"`
- Check balloon_id matches exactly (case-sensitive)

### Maps Not Loading
- Verify Google Maps API key in `.env`
- Check API key restrictions allow your domain
- Ensure JavaScript console shows no errors

## Production Deployment

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=mysql://user:password@host:port/database
GOOGLE_MAPS_API_KEY=your-production-api-key
ALLOWED_HOSTS=your-domain.com
```

### Deployment Commands
```bash
# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser --noinput
```

## API Reference

### Telemetry Data Fields
- `balloon_id`: String (required) - Unique balloon identifier
- `latitude`: Float - Latitude in decimal degrees
- `longitude`: Float - Longitude in decimal degrees
- `altitude`: Float - Altitude in meters
- `temperature`: Float - Temperature in Celsius
- `battery_level`: Float - Battery percentage (0-100)

### Response Codes
- `200`: Success
- `400`: Bad request (missing/invalid data)
- `404`: Balloon not found
- `500`: Server error

## Performance Notes

- Simulation generates ~12 data points per minute per balloon
- Dashboard updates every 10-30 seconds
- Database can handle hundreds of balloons with proper indexing
- Google Maps API has free tier limits (28,000 loads/month)

## Getting Help

- Check Django logs: `tail -f logs/django.log`
- View admin interface for data inspection
- Use browser developer tools for frontend debugging
- Test API endpoints with curl or Postman

Happy balloon tracking! 🚀🎈</content>
<parameter name="filePath">/workspaces/eclipse-mission-control/SIMULATION_GUIDE.md