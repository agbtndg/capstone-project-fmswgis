from django.db import models

class RainfallData(models.Model):
    value_mm = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=None, null=True, blank=True, db_index=True)
    station_name = models.CharField(max_length=100, default='Silay City')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

class WeatherData(models.Model):
    temperature_c = models.FloatField(default=28.5)
    humidity_percent = models.IntegerField(default=75)
    wind_speed_kph = models.FloatField(default=10)
    timestamp = models.DateTimeField(default=None, null=True, blank=True, db_index=True)
    station_name = models.CharField(max_length=100, default='Silay City')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

class TideLevelData(models.Model):
    height_m = models.FloatField(default=0.8)
    timestamp = models.DateTimeField(default=None, null=True, blank=True, db_index=True)
    station_name = models.CharField(max_length=100, default='Silay City')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

class FloodRecord(models.Model):
    event = models.CharField(max_length=200)
    date = models.DateField()
    affected_barangays = models.CharField(max_length=500)
    
    # Barangay-specific breakdown (JSON format)
    barangay_data = models.JSONField(default=dict, blank=True, help_text='Stores barangay-level breakdown of all metrics')
    
    # Total casualties (aggregated from barangay data)
    casualties_dead = models.IntegerField(default=0)
    casualties_injured = models.IntegerField(default=0)
    casualties_missing = models.IntegerField(default=0)
    
    # Total affected (aggregated from barangay data)
    affected_persons = models.IntegerField(default=0)
    affected_families = models.IntegerField(default=0)
    
    # Total houses damaged (aggregated from barangay data)
    houses_damaged_partially = models.IntegerField(default=0)
    houses_damaged_totally = models.IntegerField(default=0)
    
    # Total financial damage (aggregated from barangay data)
    damage_infrastructure_php = models.FloatField(default=0)
    damage_agriculture_php = models.FloatField(default=0)
    damage_institutions_php = models.FloatField(default=0)
    damage_private_commercial_php = models.FloatField(default=0)
    damage_total_php = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['event', 'date']),
        ]

    def __str__(self):
        return f"{self.event} - {self.date}"

class BenchmarkSettings(models.Model):
    """Store flood risk benchmark thresholds for rainfall and tide level"""
    
    # MODERATE RISK thresholds - Trigger when BOTH conditions are met
    rainfall_moderate_threshold = models.FloatField(
        default=30,
        help_text="Rainfall threshold for Moderate Risk (mm) - Moderate alert when rainfall reaches this level"
    )
    tide_moderate_threshold = models.FloatField(
        default=1.0,
        help_text="Tide level threshold for Moderate Risk (m) - Moderate alert when tide reaches this level"
    )
    
    # HIGH RISK thresholds - Trigger when BOTH conditions are met
    rainfall_high_threshold = models.FloatField(
        default=50,
        help_text="Rainfall threshold for High Risk (mm) - High alert when rainfall reaches this level"
    )
    tide_high_threshold = models.FloatField(
        default=1.5,
        help_text="Tide level threshold for High Risk (m) - High alert when tide reaches this level"
    )
    
    # Combined risk calculation method
    RISK_METHOD_CHOICES = [
        ('max', 'Maximum (Highest of both)'),
        ('rainfall_priority', 'Rainfall Priority (80% rainfall, 20% tide)'),
        ('tide_priority', 'Tide Priority (20% rainfall, 80% tide)'),
        ('equal', 'Equal Weight (50% rainfall, 50% tide)'),
    ]
    combined_risk_method = models.CharField(
        max_length=20,
        choices=RISK_METHOD_CHOICES,
        default='max',
        help_text='Method for calculating combined flood risk from rainfall and tide'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Benchmark Settings"
        verbose_name_plural = "Benchmark Settings"
    
    def __str__(self):
        return "Flood Risk Benchmark Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton benchmark settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings