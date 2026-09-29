from django.core.management.base import BaseCommand
from escalation.services import check_and_escalate_overdue_complaints

class Command(BaseCommand):
    help = "Checks all active complaints against SLA deadlines and escalates overdue tickets."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Scanning complaints for SLA breaches..."))
        count = check_and_escalate_overdue_complaints()
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully processed and escalated {count} overdue complaint(s)."))
        else:
            self.stdout.write(self.style.SUCCESS("All complaints are within their SLA deadlines. No breaches detected."))
