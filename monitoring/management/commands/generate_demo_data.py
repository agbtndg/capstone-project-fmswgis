"""
Management command to generate demo historical data for multi-year comparison.
This creates rainfall and tide data for 2023, 2024, and 2025 for demonstration purposes.

Usage:
    python manage.py generate_demo_data
    python manage.py generate_demo_data --days 90  # Generate 90 days of data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from monitoring.models import RainfallData, TideLevelData
from datetime import timedelta, datetime
import random


class Command(BaseCommand):
    help = 'Generate demo historical data for multi-year comparison (2023, 2024, 2025)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of historical data to generate (default: 90)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data',
        )

    def handle(self, *args, **options):
        days = options['days']
        clear_data = options['clear']
        
        self.stdout.write(self.style.WARNING(f'Generating {days} days of demo data for 2023, 2024, and 2025...'))
        
        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            RainfallData.objects.all().delete()
            TideLevelData.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))
        
        now = timezone.now()
        total_records = 0
        
        # Generate data for each year (2023, 2024, 2025)
        for year in [2023, 2024, 2025]:
            self.stdout.write(f'\n📅 Generating data for {year}...')
            
            # Calculate start and end dates for this year
            # Use the same month/day/hour as current time, but in the target year
            now_naive = now.replace(tzinfo=None)
            
            # Create end date in target year (same as current date/time but in target year)
            try:
                end_date = datetime(year, now_naive.month, now_naive.day, 
                                   now_naive.hour, now_naive.minute, now_naive.second)
            except ValueError:
                # Handle Feb 29 in non-leap years
                end_date = datetime(year, now_naive.month, 28, 
                                   now_naive.hour, now_naive.minute, now_naive.second)
            
            # Make it timezone-aware
            end_date = timezone.make_aware(end_date)
            
            # Calculate start date (days before end date)
            start_date = end_date - timedelta(days=days)
            
            rainfall_count = 0
            tide_count = 0
            
            # Generate hourly rainfall data
            current_time = start_date
            while current_time <= end_date:
                # Generate realistic rainfall patterns (0-50mm, with occasional spikes)
                base_rainfall = random.uniform(0, 5)
                
                # Add weather patterns (rainy days)
                if random.random() < 0.2:  # 20% chance of rainy period
                    base_rainfall += random.uniform(10, 40)
                
                # Seasonal variation (higher in certain months)
                month = current_time.month
                if month in [6, 7, 8, 9]:  # Rainy season
                    base_rainfall *= random.uniform(1.2, 2.0)
                
                RainfallData.objects.create(
                    value_mm=round(base_rainfall, 2),
                    station_name=f'Open-Meteo (Silay City) - Demo {year}',
                    timestamp=current_time
                )
                rainfall_count += 1
                
                current_time += timedelta(hours=1)
            
            # Generate 3-hourly tide data
            current_time = start_date
            while current_time <= end_date:
                # Generate realistic tidal patterns (sinusoidal with noise)
                # Tides cycle roughly every 12.4 hours
                hours_from_start = (current_time - start_date).total_seconds() / 3600
                tide_cycle = (hours_from_start % 12.4) / 12.4 * 2 * 3.14159
                
                # Base tide level oscillating between -0.5m and 1.8m
                base_tide = 0.65 + 1.15 * (0.5 + 0.5 * random.uniform(-1, 1) * 0.3)
                
                # Add tidal pattern
                tide_level = base_tide + 0.4 * (1 + random.uniform(-0.2, 0.2))
                
                # Clamp to reasonable range
                tide_level = max(-0.5, min(2.0, tide_level))
                
                TideLevelData.objects.create(
                    height_m=round(tide_level, 3),
                    station_name=f'WorldTides - Cebu City - Demo {year}',
                    timestamp=current_time
                )
                tide_count += 1
                
                current_time += timedelta(hours=3)
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ {year}: Created {rainfall_count} rainfall records and {tide_count} tide records'))
            total_records += rainfall_count + tide_count
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Demo data generation completed!'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total records created: {total_records:,}'))
        self.stdout.write(self.style.WARNING(f'\n💡 You can now use the multi-year comparison feature in the monitoring dashboard!'))
        self.stdout.write(self.style.WARNING(f'💡 Select years from the dropdown and click "Apply Comparison" to see overlapping trends.'))
