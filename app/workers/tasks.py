import smtplib
from email.mime.text import MIMEText
from arq.connections import RedisSettings
from app.config import settings
import structlog

logger = structlog.get_logger()


async def send_notification_email(ctx, to: str, subject: str, body: str) -> None:
    """Send email via SMTP.

    Enqueue with:
        await queue.enqueue_job("send_notification_email", to, subject, body)
    """
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to

    if not settings.SMTP_HOST:
        logger.warning("smtp_not_configured", to=to, subject=subject)
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(settings.FROM_EMAIL, to, msg.as_string())

    logger.info("email_sent", to=to, subject=subject)


async def process_image(ctx, image_url: str, item_id: str) -> None:
    """Resize/optimize item image and re-upload to S3.

    Enqueue with:
        await queue.enqueue_job("process_image", image_url, item_id)
    """
    logger.info("image_processing_started", item_id=item_id, url=image_url)
    # TODO: download with httpx, resize with Pillow, re-upload to S3
    logger.info("image_processing_done", item_id=item_id)


async def send_payment_notification(ctx, user_email: str, order_id: str, status: str) -> None:
    """Notify buyer/seller of payment status change."""
    subject = f"Payment {status} — Order {order_id[:8]}"
    body = f"<p>Your payment for order <strong>{order_id}</strong> is now <strong>{status}</strong>.</p>"
    await send_notification_email(ctx, to=user_email, subject=subject, body=body)


class WorkerSettings:
    functions = [send_notification_email, process_image, send_payment_notification]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 300
    keep_result = 3600  # seconds to keep job results in Redis
