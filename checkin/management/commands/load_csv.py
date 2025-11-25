# from django.core.management.base import BaseCommand
import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from checkin.models import Attendee, CheckInSession

class Command(BaseCommand):
    help = 'Load attendees from CSV file into a specific session'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')
        parser.add_argument(
            '--session',
            type=int,
            help='Optional session ID. If not provided, a new session is created.'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        session_id = kwargs.get('session')

        # If no session specified → create a new one automatically
        if session_id:
            try:
                session = CheckInSession.objects.get(id=session_id)
            except CheckInSession.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Session ID {session_id} not found"))
                return
        else:
            session = CheckInSession.objects.create(name="Imported Session")
            self.stdout.write(self.style.WARNING(
                f"No session given → created session #{session.id} ({session.name})"
            ))

        created_count = 0
        updated_count = 0

        with open(file_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                qr_code = (row.get('qr_code') or row.get('qr') or '').strip()
                if not qr_code:
                    continue

                uid = (row.get('uid') or row.get('id') or '').strip()
                nom = (row.get('nom') or '').strip()
                prenom = (row.get('prenom') or '').strip()
                tel = (row.get('tel') or row.get('telephone') or '').strip()

                # Parse prix (optional)
                raw_prix = row.get('prix')
                try:
                    prix = Decimal(raw_prix) if raw_prix and raw_prix.strip() else None
                except:
                    prix = None

                obj, created = Attendee.objects.update_or_create(
                    session=session,
                    qr_code=qr_code,
                    defaults={
                        'uid': uid,
                        'nom': nom,
                        'prenom': prenom,
                        'tel': tel,
                        'prix': prix,
                        'checked_in': False,
                        'checkin_date': None,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"CSV loaded successfully → {created_count} created, {updated_count} updated"
        ))
        self.stdout.write(self.style.SUCCESS(f"Session used: {session.id} - {session.name}"))
