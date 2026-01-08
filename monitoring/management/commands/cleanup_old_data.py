"""
Management command to clean up old monitoring data.
This helps prevent database bloat by removing old rainfall, weather, and tide records.

Usage:
    python manage.py cleanup_old_data --days 90
    python manage.py cleanup_old_data --days 180 --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from monitoring.models import RainfallData, WeatherData, TideLevelData
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up old monitoring data to prevent database bloat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete data older than this many days (default: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--keep-daily',
            action='store_true',
            help='Keep one record per day for historical data beyond retention period',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        keep_daily = options['keep_daily']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(self.style.WARNING(
            f'\n{"DRY RUN: " if dry_run else ""}Cleaning up data older than {days} days (before {cutoff_date.strftime("%Y-%m-%d %H:%M")})\n'
        ))
        
        # Count records to be deleted
        rainfall_count = RainfallData.objects.filter(timestamp__lt=cutoff_date).count()
        weather_count = WeatherData.objects.filter(timestamp__lt=cutoff_date).count()
        tide_count = TideLevelData.objects.filter(timestamp__lt=cutoff_date).count()
        
        total_count = rainfall_count + weather_count + tide_count
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ No old data to clean up'))
            return
        
        # Display summary
        self.stdout.write(f'Records to be deleted:')
        self.stdout.write(f'  - Rainfall data: {rainfall_count:,} records')
        self.stdout.write(f'  - Weather data: {weather_count:,} records')
        self.stdout.write(f'  - Tide data: {tide_count:,} records')
        self.stdout.write(f'  Total: {total_count:,} records\n')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('✓ Dry run completed. No data was deleted.'))
            return
        
        # Perform deletion
        if keep_daily:
            self.stdout.write(self.style.WARNING('⚠ Keep-daily feature not yet implemented. Deleting all old data.'))
        
        deleted_counts = {
            'rainfall': 0,
            'weather': 0,
            'tide': 0
        }
        
        # Delete in batches to avoid memory issues
        batch_size = 1000
        
        # Delete rainfall data
        while True:
            batch = list(RainfallData.objects.filter(timestamp__lt=cutoff_date).values_list('id', flat=True)[:batch_size])
            if not batch:
                break
            count = RainfallData.objects.filter(id__in=batch).delete()[0]
            deleted_counts['rainfall'] += count
            self.stdout.write(f'  Deleted {deleted_counts["rainfall"]:,} rainfall records...', ending='\r')
        
        self.stdout.write(f'  ✓ Deleted {deleted_counts["rainfall"]:,} rainfall records    ')
        
        # Delete weather data
        while True:
            batch = list(WeatherData.objects.filter(timestamp__lt=cutoff_date).values_list('id', flat=True)[:batch_size])
            if not batch:
                break
            count = WeatherData.objects.filter(id__in=batch).delete()[0]
            deleted_counts['weather'] += count
            self.stdout.write(f'  Deleted {deleted_counts["weather"]:,} weather records...', ending='\r')
        
        self.stdout.write(f'  ✓ Deleted {deleted_counts["weather"]:,} weather records    ')
        
        # Delete tide data
        while True:
            batch = list(TideLevelData.objects.filter(timestamp__lt=cutoff_date).values_list('id', flat=True)[:batch_size])
            if not batch:
                break
            count = TideLevelData.objects.filter(id__in=batch).delete()[0]
            deleted_counts['tide'] += count
            self.stdout.write(f'  Deleted {deleted_counts["tide"]:,} tide records...', ending='\r')
        
        self.stdout.write(f'  ✓ Deleted {deleted_counts["tide"]:,} tide records    ')
        
        total_deleted = sum(deleted_counts.values())
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully deleted {total_deleted:,} records'))
        
        # Show remaining data
        remaining_rainfall = RainfallData.objects.count()
        remaining_weather = WeatherData.objects.count()
        remaining_tide = TideLevelData.objects.count()
        
        self.stdout.write(f'\nRemaining records:')
        self.stdout.write(f'  - Rainfall: {remaining_rainfall:,} records')
        self.stdout.write(f'  - Weather: {remaining_weather:,} records')
        self.stdout.write(f'  - Tide: {remaining_tide:,} records')
