import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications.utils import send_notification_to_user

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        send_notification_to_user(
            user_id=instance.id,
            title="Welcome!",
            body=f"Hi {instance.username}, thanks for joining.",
            type_="success",
            # data={"action": "onboarding"},
            extra={"action": "onboarding"},
        )
    except Exception:
        logger.exception("Welcome notification failed for users %s", instance.id)
        
@receiver(post_save, sender=User)
def on_user_updated(sender, instance, created, **kwargs):
    if created:
        return
    # Example: notify when email changes (track previous value yourself; simplefied)
    # here we just fire a generic info notification on any update for demo
    try:
        send_notification_to_user(
            user_id=instance.id,
            title="Profile updated",
            body="Your profile was updated successfully.",
            type_="info",
        )
    except Exception:
        logger.exception("Update notification failed for user %s", instance.id)