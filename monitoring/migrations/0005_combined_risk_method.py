# Migration to add combined_risk_method field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_benchmarksettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='benchmarksettings',
            name='alert_heavy_rain_threshold',
        ),
        migrations.RemoveField(
            model_name='benchmarksettings',
            name='alert_total_precipitation_threshold',
        ),
        migrations.AddField(
            model_name='benchmarksettings',
            name='combined_risk_method',
            field=models.CharField(
                choices=[
                    ('max', 'Maximum (Highest of both)'),
                    ('rainfall_priority', 'Rainfall Priority (80% rainfall, 20% tide)'),
                    ('tide_priority', 'Tide Priority (20% rainfall, 80% tide)'),
                    ('equal', 'Equal Weight (50% rainfall, 50% tide)'),
                ],
                default='max',
                help_text='Method for calculating combined flood risk from rainfall and tide',
                max_length=20,
            ),
        ),
    ]
