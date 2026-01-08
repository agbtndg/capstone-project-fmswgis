"""
Management command to restore archived records.

This command restores archived records back to active status.

Usage:
    python manage.py restore_archived_records --all --dry-run
    python manage.py restore_archived_records --all --execute
    python manage.py restore_archived_records --type=assessments --execute
    python manage.py restore_archived_records --date-from=2023-01-01 --date-to=2023-12-31 --execute
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from datetime import datetime
from maps.models import AssessmentRecord, ReportRecord, CertificateRecord, FloodRecordActivity
from users.models import UserLog


class Command(BaseCommand):
    help = 'Restore archived records back to active status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Restore all archived records'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['assessments', 'reports', 'certificates', 'flood_activities', 'user_logs'],
            help='Restore only specific type of records'
        )
        parser.add_argument(
            '--date-from',
            type=str,
            help='Restore records from this date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--date-to',
            type=str,
            help='Restore records up to this date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be restored without actually restoring'
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Actually perform the restoration (required to make changes)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        execute = options['execute']
        restore_all = options['all']
        record_type = options['type']
        date_from = options['date_from']
        date_to = options['date_to']

        # Validate options
        if not dry_run and not execute:
            raise CommandError(
                'You must specify either --dry-run or --execute. '
                'Use --dry-run first to preview what will be restored.'
            )

        if dry_run and execute:
            raise CommandError('Cannot use both --dry-run and --execute together.')

        if not restore_all and not record_type and not date_from:
            raise CommandError(
                'You must specify either --all, --type, or --date-from/--date-to'
            )

        # Parse dates if provided
        date_from_obj = None
        date_to_obj = None
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid date-from format. Use YYYY-MM-DD')
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid date-to format. Use YYYY-MM-DD')

        self.stdout.write(self.style.WARNING(
            f'\n{"="*70}\n'
            f'RESTORING ARCHIVED RECORDS\n'
            f'MODE: {"DRY RUN (preview only)" if dry_run else "EXECUTE (will restore)"}\n'
            f'{"="*70}\n'
        ))

        # Count records to restore
        counts = self._count_records(restore_all, record_type, date_from_obj, date_to_obj)
        
        # Display summary
        self._display_summary(counts)

        # If dry run, stop here
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Dry run complete. No records were modified.\n'
                    f'  Run with --execute to perform the restoration.\n'
                )
            )
            return

        # Confirm before executing
        if not self._confirm_restoration(counts):
            self.stdout.write(self.style.WARNING('Restoration cancelled.'))
            return

        # Perform restoration
        self.stdout.write(self.style.MIGRATE_HEADING('\nRestoring records...'))
        restored_counts = self._restore_records(restore_all, record_type, date_from_obj, date_to_obj)

        # Display results
        self._display_results(restored_counts)

    def _get_queryset(self, model, date_from, date_to):
        """Get queryset of archived records for a model."""
        qs = model.objects.filter(is_archived=True)
        if date_from:
            qs = qs.filter(timestamp__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__lte=date_to)
        return qs

    def _count_records(self, restore_all, record_type, date_from, date_to):
        """Count records that would be restored."""
        counts = {
            'assessments': 0,
            'reports': 0,
            'certificates': 0,
            'flood_activities': 0,
            'user_logs': 0,
        }

        if restore_all or record_type == 'assessments':
            counts['assessments'] = self._get_queryset(AssessmentRecord, date_from, date_to).count()
        
        if restore_all or record_type == 'reports':
            counts['reports'] = self._get_queryset(ReportRecord, date_from, date_to).count()
        
        if restore_all or record_type == 'certificates':
            counts['certificates'] = self._get_queryset(CertificateRecord, date_from, date_to).count()
        
        if restore_all or record_type == 'flood_activities':
            counts['flood_activities'] = self._get_queryset(FloodRecordActivity, date_from, date_to).count()
        
        if restore_all or record_type == 'user_logs':
            counts['user_logs'] = self._get_queryset(UserLog, date_from, date_to).count()

        counts['total'] = sum(counts.values())
        return counts

    def _display_summary(self, counts):
        """Display summary of what will be restored."""
        self.stdout.write(self.style.WARNING('\nRecords to restore:\n'))
        
        self.stdout.write(f'  • Assessment Records:      {counts["assessments"]:>6,}')
        self.stdout.write(f'  • Report Records:          {counts["reports"]:>6,}')
        self.stdout.write(f'  • Certificate Records:     {counts["certificates"]:>6,}')
        self.stdout.write(f'  • Flood Record Activities: {counts["flood_activities"]:>6,}')
        self.stdout.write(f'  • User Activity Logs:      {counts["user_logs"]:>6,}')
        self.stdout.write(self.style.WARNING(f'  {"-"*35}'))
        self.stdout.write(self.style.MIGRATE_HEADING(f'  TOTAL:                     {counts["total"]:>6,}\n'))

    def _confirm_restoration(self, counts):
        """Ask for confirmation before restoring."""
        if counts['total'] == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No records to restore.'))
            return False

        self.stdout.write(
            self.style.WARNING(
                f'\n⚠️  You are about to restore {counts["total"]:,} archived records.\n'
                f'   They will appear again in normal activity views.\n'
            )
        )
        
        response = input('Type "yes" to proceed, or "no" to cancel: ')
        return response.lower() == 'yes'

    @transaction.atomic
    def _restore_records(self, restore_all, record_type, date_from, date_to):
        """Perform the actual restoration."""
        restored_counts = {}

        if restore_all or record_type == 'assessments':
            count = self._get_queryset(AssessmentRecord, date_from, date_to).update(
                is_archived=False, archived_at=None
            )
            restored_counts['assessments'] = count
            self.stdout.write(f'  ✓ Restored {count:,} assessment records')

        if restore_all or record_type == 'reports':
            count = self._get_queryset(ReportRecord, date_from, date_to).update(
                is_archived=False, archived_at=None
            )
            restored_counts['reports'] = count
            self.stdout.write(f'  ✓ Restored {count:,} report records')

        if restore_all or record_type == 'certificates':
            count = self._get_queryset(CertificateRecord, date_from, date_to).update(
                is_archived=False, archived_at=None
            )
            restored_counts['certificates'] = count
            self.stdout.write(f'  ✓ Restored {count:,} certificate records')

        if restore_all or record_type == 'flood_activities':
            count = self._get_queryset(FloodRecordActivity, date_from, date_to).update(
                is_archived=False, archived_at=None
            )
            restored_counts['flood_activities'] = count
            self.stdout.write(f'  ✓ Restored {count:,} flood record activities')

        if restore_all or record_type == 'user_logs':
            count = self._get_queryset(UserLog, date_from, date_to).update(
                is_archived=False, archived_at=None
            )
            restored_counts['user_logs'] = count
            self.stdout.write(f'  ✓ Restored {count:,} user activity logs')

        restored_counts['total'] = sum(restored_counts.values())
        return restored_counts

    def _display_results(self, counts):
        """Display final results."""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*70}\n'
                f'✓ RESTORATION COMPLETE\n'
                f'{"="*70}\n'
                f'Total records restored: {counts["total"]:,}\n\n'
                f'What happens next:\n'
                f'  • Restored records now appear in normal activity views\n'
                f'  • They are included in all filters and searches\n'
                f'  • They can be archived again if needed\n'
                f'{"="*70}\n'
            )
        )
