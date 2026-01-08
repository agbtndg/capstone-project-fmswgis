from django.contrib import admin
from .models import RainfallData, WeatherData, TideLevelData, FloodRecord, BenchmarkSettings


@admin.register(BenchmarkSettings)
class BenchmarkSettingsAdmin(admin.ModelAdmin):
    """Admin interface for BenchmarkSettings"""
    fieldsets = (
        ('Rainfall Benchmarks (mm)', {
            'fields': ('rainfall_moderate_threshold', 'rainfall_high_threshold')
        }),
        ('Tide Level Benchmarks (m)', {
            'fields': ('tide_moderate_threshold', 'tide_high_threshold')
        }),
        ('Risk Calculation Method', {
            'fields': ('combined_risk_method',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Only allow one BenchmarkSettings record"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of BenchmarkSettings"""
        return False


admin.site.register(RainfallData)
admin.site.register(WeatherData)
admin.site.register(TideLevelData)
admin.site.register(FloodRecord)