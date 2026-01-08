# Generated migration for BenchmarkSettings model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_floodrecord_remove_rainfalldata_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rainfall_moderate_threshold', models.FloatField(default=30, help_text='Rainfall threshold (mm) for moderate risk')),
                ('rainfall_high_threshold', models.FloatField(default=50, help_text='Rainfall threshold (mm) for high risk')),
                ('tide_moderate_threshold', models.FloatField(default=1.0, help_text='Tide threshold (m) for moderate risk')),
                ('tide_high_threshold', models.FloatField(default=1.5, help_text='Tide threshold (m) for high risk')),
                ('alert_heavy_rain_threshold', models.FloatField(default=15, help_text='Daily rainfall threshold (mm) for heavy rain alert')),
                ('alert_total_precipitation_threshold', models.FloatField(default=50, help_text='7-day cumulative rainfall threshold (mm) for precipitation alert')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'verbose_name': 'Benchmark Settings',
                'verbose_name_plural': 'Benchmark Settings',
            },
        ),
    ]
