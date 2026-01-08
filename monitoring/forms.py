from django import forms
from django.core.exceptions import ValidationError
from .models import FloodRecord
from datetime import datetime
from django.utils import timezone

# Updated BARANGAYS list with real Silay City barangays
BARANGAYS = [
    ('Balaring', 'Balaring'),
    ('Barangay I (Pob.)', 'Barangay I (Pob.)'),
    ('Barangay II (Pob.)', 'Barangay II (Pob.)'),
    ('Barangay III (Pob.)', 'Barangay III (Pob.)'),
    ('Barangay IV (Pob.)', 'Barangay IV (Pob.)'),
    ('Barangay V (Pob.)', 'Barangay V (Pob.)'),
    ('Barangay VI Pob. (Hawaiian)', 'Barangay VI Pob. (Hawaiian)'),
    ('Eustaquio Lopez', 'Eustaquio Lopez'),
    ('Guimbala-on', 'Guimbala-on'),
    ('Guinhalaran', 'Guinhalaran'),
    ('Kapitan Ramon', 'Kapitan Ramon'),
    ('Lantad', 'Lantad'),
    ('Mambulac', 'Mambulac'),
    ('Rizal', 'Rizal'),
    ('Bagtic', 'Bagtic'),
    ('Patag', 'Patag'),
]

EVENT_TYPES = [
    ('Flood', 'Flood'),
    ('Flash Flood', 'Flash Flood'),
]

class FloodRecordForm(forms.ModelForm):
    affected_barangays = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'id_affected_barangays', 
            'readonly': 'readonly',
            'placeholder': 'No barangays selected yet'
        }),
        required=True,
        help_text='Select barangays from the dropdown below.',
        error_messages={
            'required': 'Please select at least one affected barangay.'
        }
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': datetime.now().strftime('%Y-%m-%d')
        }),
        help_text='Select the date of the flood event.',
        error_messages={
            'required': 'Please provide the date of the flood event.',
            'invalid': 'Please enter a valid date.'
        }
    )
    
    event = forms.ChoiceField(
        choices=EVENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose the type of flood event.',
        error_messages={
            'required': 'Please select an event type.'
        }
    )

    class Meta:
        model = FloodRecord
        fields = ['event', 'date', 'affected_barangays']
        widgets = {}

    def clean_affected_barangays(self):
        """Validate affected barangays field."""
        affected_barangays = self.cleaned_data.get('affected_barangays', '').strip()
        
        if not affected_barangays:
            raise ValidationError("At least one barangay must be selected.")
        
        # Split and validate each barangay
        barangay_list = [b.strip() for b in affected_barangays.split(',') if b.strip()]
        
        if not barangay_list:
            raise ValidationError("At least one barangay must be selected.")
        
        # Get valid barangay names
        valid_barangays = [b[0] for b in BARANGAYS]
        
        # Check if all selected barangays are valid
        invalid_barangays = [b for b in barangay_list if b not in valid_barangays]
        if invalid_barangays:
            raise ValidationError(f"Invalid barangay names: {', '.join(invalid_barangays)}")
        
        # Remove duplicates and rejoin
        unique_barangays = list(dict.fromkeys(barangay_list))
        return ', '.join(unique_barangays)

    def clean_date(self):
        """Validate that the date is not in the future."""
        date = self.cleaned_data.get('date')
        
        if date and date > timezone.now().date():
            raise ValidationError("The flood event date cannot be in the future.")
        
        return date