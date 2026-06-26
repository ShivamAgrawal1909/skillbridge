from app.config import settings


def send_whatsapp_notification(phone: str, message: str):
    pass


def run_provider_matching(request_id: str):
    from app.config import settings
    if not settings.REDIS_URL:
        return

    import asyncio
    from app.database import SessionLocal
    from app.services.request import match_providers

    async def _run():
        async with SessionLocal() as db:
            matched = await match_providers(request_id, db)
            for provider in matched:
                print(f"Matched provider: {provider.id} for request: {request_id}")

    asyncio.run(_run())


if settings.REDIS_URL:
    from app.worker import celery

    if celery:
        send_whatsapp_notification = celery.task(
            bind=True, max_retries=3
        )(send_whatsapp_notification)

        run_provider_matching = celery.task(
            bind=True, max_retries=3
        )(run_provider_matching)