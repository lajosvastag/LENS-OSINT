from celery import Celery
from app.core.config import settings

celery_app = Celery("lens", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", task_track_started=True)

@celery_app.task(name="lens.health_check")
def health_check() -> dict[str, str]:
    return {"status": "ok", "worker": "lens"}
