"""
Management command to archive old activity records.

This command marks records older than a specified number of years as archived.
Archived records are excluded from normal views but remain accessible.

Usage:
    python manage.py archive_old_records --years=2 --dry-run
    python manage.py archive_old_records --years=2 --execute
    python manage.py archive_old_records --years=3 --execute --include-logs
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from maps.models import AssessmentRecord, ReportRecord, CertificateRecord, FloodRecordActivity
from users.models import UserLog


class Command(BaseCommand):
    help = 'Archive old activity records (marks them as archived, does not delete)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=int,
            default=2,
            help='Archive records older than this many years (default: 2)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be archived without actually archiving'
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Actually perform the archiving (required to make changes)'
        )
        parser.add_argument(
            '--include-logs',
            action='store_true',
            help='Also archive user activity logs (default: skip logs)'
        )

    def handle(self, *args, **options):
        years = options['years']
        dry_run = options['dry_run']
        execute = options['execute']
        include_logs = options['include_logs']

        # Validate options
        if not dry_run and not execute:
            raise CommandError(
                'You must specify either --dry-run or --execute. '
                'Use --dry-run first to preview what will be archived.'
            )

        if dry_run and execute:
            raise CommandError('Cannot use both --dry-run and --execute together.')

        if years < 1:
            raise CommandError('Years must be at least 1.')

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=365 * years)
        
        self.stdout.write(self.style.WARNING(
            f'\n{"="*70}\n'
            f'ARCHIVING RECORDS OLDER THAN: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'MODE: {"DRY RUN (preview only)" if dry_run else "EXECUTE (will archive)"}\n'
            f'{"="*70}\n'
        ))

        # Count records to archive
        counts = self._count_records(cutoff_date, include_logs)
        
        # Display summary
        self._display_summary(counts, cutoff_date, years)

        # If dry run, stop here
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Dry run complete. No records were modified.\n'
                    f'  Run with --execute to perform the archiving.\n'
                )
            )
            return

        # Confirm before executing
        if not self._confirm_archiving(counts):
            self.stdout.write(self.style.WARNING('Archiving cancelled.'))
            return

        # Perform archiving
        self.stdout.write(self.style.MIGRATE_HEADING('\nArchiving records...'))
        archived_counts = self._archive_records(cutoff_date, include_logs)

        # Display results
        self._display_results(archived_counts)

    def _count_records(self, cutoff_date, include_logs):
        """Count records that would be archived."""
        counts = {
            'assessments': AssessmentRecord.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).count(),
            'reports': ReportRecord.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).count(),
            'certificates': CertificateRecord.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).count(),
            'flood_activities': FloodRecordActivity.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).count(),
        }
        
        if include_logs:
            counts['user_logs'] = UserLog.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).count()
        else:
            counts['user_logs'] = 0

        counts['total'] = sum(counts.values())
        return counts

    def _display_summary(self, counts, cutoff_date, years):
        """Display summary of what will be archived."""
        self.stdout.write(self.style.WARNING(
            f'\nRecords to archive (older than {years} year{"s" if years > 1 else ""}):\n'
        ))
        
        self.stdout.write(f'  • Assessment Records:      {counts["assessments"]:>6,}')
        self.stdout.write(f'  • Report Records:          {counts["reports"]:>6,}')
        self.stdout.write(f'  • Certificate Records:     {counts["certificates"]:>6,}')
        self.stdout.write(f'  • Flood Record Activities: {counts["flood_activities"]:>6,}')
        self.stdout.write(f'  • User Activity Logs:      {counts["user_logs"]:>6,}')
        self.stdout.write(self.style.WARNING(f'  {"-"*35}'))
        self.stdout.write(self.style.MIGRATE_HEADING(f'  TOTAL:                     {counts["total"]:>6,}\n'))

    def _confirm_archiving(self, counts):
        """Ask for confirmation before archiving."""
        if counts['total'] == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No records to archive.'))
            return False

        self.stdout.write(
            self.style.WARNING(
                f'\n⚠️  You are about to archive {counts["total"]:,} records.\n'
                f'   Archived records will not appear in normal views but can be restored.\n'
            )
        )
        
        response = input('Type "yes" to proceed, or "no" to cancel: ')
        return response.lower() == 'yes'

    @transaction.atomic
    def _archive_records(self, cutoff_date, include_logs):
        """Perform the actual archiving."""
        now = timezone.now()
        archived_counts = {}

        # Archive assessments
        assessment_count = AssessmentRecord.objects.filter(
            timestamp__lt=cutoff_date,
            is_archived=False
        ).update(is_archived=True, archived_at=now)
        archived_counts['assessments'] = assessment_count
        self.stdout.write(f'  ✓ Archived {assessment_count:,} assessment records')

        # Archive reports
        report_count = ReportRecord.objects.filter(
            timestamp__lt=cutoff_date,
            is_archived=False
        ).update(is_archived=True, archived_at=now)
        archived_counts['reports'] = report_count
        self.stdout.write(f'  ✓ Archived {report_count:,} report records')

        # Archive certificates
        certificate_count = CertificateRecord.objects.filter(
            timestamp__lt=cutoff_date,
            is_archived=False
        ).update(is_archived=True, archived_at=now)
        archived_counts['certificates'] = certificate_count
        self.stdout.write(f'  ✓ Archived {certificate_count:,} certificate records')

        # Archive flood activities
        flood_count = FloodRecordActivity.objects.filter(
            timestamp__lt=cutoff_date,
            is_archived=False
        ).update(is_archived=True, archived_at=now)
        archived_counts['flood_activities'] = flood_count
        self.stdout.write(f'  ✓ Archived {flood_count:,} flood record activities')

        # Archive user logs if requested
        if include_logs:
            log_count = UserLog.objects.filter(
                timestamp__lt=cutoff_date,
                is_archived=False
            ).update(is_archived=True, archived_at=now)
            archived_counts['user_logs'] = log_count
            self.stdout.write(f'  ✓ Archived {log_count:,} user activity logs')
        else:
            archived_counts['user_logs'] = 0

        archived_counts['total'] = sum(archived_counts.values())
        return archived_counts

    def _display_results(self, counts):
        """Display final results."""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*70}\n'
                f'✓ ARCHIVING COMPLETE\n'
                f'{"="*70}\n'
                f'Total records archived: {counts["total"]:,}\n\n'
                f'What happens next:\n'
                f'  • Archived records are excluded from normal activity views\n'
                f'  • They remain in the database and can be restored if needed\n'
                f'  • Database performance should improve for recent data queries\n'
                f'  • You can view archived records using the "View Archives" feature\n'
                f'{"="*70}\n'
            )
        )
