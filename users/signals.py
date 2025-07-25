from django.core.mail import send_mail
from users.models import Order, Product
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer




@receiver([post_save, post_delete], sender=Product)
def broadcast_product_updates(sender, instance, **kwargs):
    """
    Update the product list in real-time when a product is created, deleted.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "products",
        {
            "type": "product.update",
        }
    )


@receiver(post_save, sender=Order)
def send_order_status_update(sender, instance, created, **kwargs):
    """
    If an order is created or updated, send an email notification to the user.
    """
    if not created:
        subject = f"Your order {instance.id} status has changed"
        message = f"Hi {instance.user.username},\n\nYour order status is now: {instance.status}"
        send_mail(subject, message, 'noreply@yourshop.com', [instance.user.email])
