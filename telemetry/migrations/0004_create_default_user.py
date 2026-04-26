# Generated manually to create default user
from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_default_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    # Create the user if it doesn't already exist
    if not User.objects.filter(username='scouts').exists():
        User.objects.create(
            username='scouts',
            password=make_password('scouts'),
            is_staff=True,
            is_superuser=False
        )

def remove_default_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='scouts').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('telemetry', '0003_alter_telemetrydata_options_alter_balloon_balloon_id_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_default_user, remove_default_user),
    ]
