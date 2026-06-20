from app.worker import celery


@celery.task(bind=True, max_retries=3)
def send_whatsapp_notification(self, phone: str, message: str):
    # will be implemented in Phase 7
    pass


@celery.task(bind=True, max_retries=3)
def run_provider_matching(self, request_id: str):
    # will be implemented in Phase 5
    pass
