try:
    from celery import shared_task
    from .services import check_and_escalate_overdue_complaints

    @shared_task
    def celery_check_escalations_task():
        return check_and_escalate_overdue_complaints()
except Exception:
    pass
