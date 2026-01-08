import os
import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import fromstr
from ...models import Barangay, FloodSusceptibility

class Command(BaseCommand):
    help = 'Loads GeoJSON files into Barangay and FloodSusceptibility models'

    def handle(self, *args, **options):
        # Get the directory where this command is located, then navigate to maps/data
        # File structure: maps/management/commands/load_shapefiles.py
        # We need: maps/data/
        command_dir = os.path.dirname(os.path.abspath(__file__))  # maps/management/commands
        maps_dir = os.path.dirname(os.path.dirname(command_dir))  # maps
        data_dir = os.path.join(maps_dir, 'data')
        
        barangay_file = os.path.join(data_dir, 'silay_barangay_map.geojson')
        flood_file = os.path.join(data_dir, 'silay_flood_map.geojson')

        self.stdout.write(f'Loading from: {data_dir}')

        # Load Barangay data
        if os.path.exists(barangay_file):
            self.stdout.write(f'Loading barangay data from {barangay_file}...')
            with open(barangay_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for feature in data['features']:
                    props = feature['properties']
                    geom = fromstr(json.dumps(feature['geometry']))
                    Barangay.objects.update_or_create(
                        id=props['id'],
                        defaults={
                            'name': props['name'],
                            'parent_id': props['parent_id'],
                            'geometry': geom
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(data["features"])} barangays'))
        else:
            self.stdout.write(self.style.ERROR(f'Barangay file not found: {barangay_file}'))

        # Load FloodSusceptibility data
        if os.path.exists(flood_file):
            self.stdout.write(f'Loading flood susceptibility data from {flood_file}...')
            with open(flood_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = 0
                for feature in data['features']:
                    props = feature['properties']
                    geom = fromstr(json.dumps(feature['geometry']))
                    FloodSusceptibility.objects.update_or_create(
                        lgu=props.get('LGU', 'Silay City'),
                        psgc_lgu=props.get('PSGC_LGU', '64526000'),
                        haz_class=props.get('HazClass', 'Flooding'),
                        haz_code=props.get('HazCode', 'LF'),  # Default to LF if missing
                        haz_area_ha=props.get('HazArea_Ha', 0.0),
                        defaults={
                            'geometry': geom
                        }
                    )
                    count += 1
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} flood susceptibility records'))
        else:
            self.stdout.write(self.style.ERROR(f'Flood file not found: {flood_file}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded all shapefiles'))