from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_image_size(image):
    """Validate uploaded image size (max 5MB)"""
    if image.size > 5 * 1024 * 1024:  # 5MB in bytes
        raise ValidationError('Image file size must be less than 5MB.')


def validate_image_dimensions(image):
    """Validate uploaded image dimensions (max 4000x4000 pixels)"""
    try:
        from PIL import Image
        img = Image.open(image)
        width, height = img.size
        if width > 4000 or height > 4000:
            raise ValidationError('Image dimensions must be less than 4000x4000 pixels.')
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


class CustomUser(AbstractUser):
    POSITION_CHOICES = [
        ("officer_planning", "DRRMO OFFICER II PLANNING & RESEARCH"),
        ("planning_assistant", "PLANNING ASSISTANT"),
        ("officer_operation", "DRRMO OFFICER II OPERATION & WARNING"),
        ("eoc", "EMERGENCY OPERATION CENTER"),
        ("monitoring_alert", "MONITORING ALERT & WARNING SYSTEM"),
        ("others", "Others"),
    ]

    staff_id = models.CharField(max_length=10, unique=True, verbose_name="Staff ID")
    is_approved = models.BooleanField(default=False, verbose_name="Approved")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default="others", verbose_name="Position")
    custom_position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Custom Position")
    contact_number = models.CharField(max_length=11, blank=True, verbose_name="Contact Number")
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name="Emergency Contact")
    emergency_number = models.CharField(max_length=11, blank=True, verbose_name="Emergency Contact Number")
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        null=True, 
        blank=True, 
        verbose_name="Profile Image",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size,
            validate_image_dimensions
        ],
        help_text="Upload a profile image (JPG, PNG, or GIF, max 5MB, max 4000x4000px)"
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

class UserLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="User")
    action = models.CharField(max_length=100, verbose_name="Action")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    is_archived = models.BooleanField(default=False, verbose_name="Archived", db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True, verbose_name="Archived Date/Time")

    class Meta:
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['is_archived', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        
    @classmethod
    def get_recent_failures(cls, username, ip_address, minutes=30):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            username=username,
            ip_address=ip_address,
            timestamp__gte=cutoff,
            success=False
        ).count()