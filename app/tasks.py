import asyncio

from app.worker import celery


@celery.task(bind=True, max_retries=3)
def send_whatsapp_notification(self, phone: str, message: str):
    # Phase 7 mein implement hoga
    pass


@celery.task(bind=True, max_retries=3)
def run_provider_matching(self, request_id: str):
    from app.database import SessionLocal
    from app.services.request import match_providers

    async def _run():
        async with SessionLocal() as db:
            matched = await match_providers(request_id, db)
            for provider in matched:
                print(f"Matched provider: {provider.id} for request: {request_id}")
                # Phase 7 mein WhatsApp notification yahan aayega

    asyncio.run(_run())