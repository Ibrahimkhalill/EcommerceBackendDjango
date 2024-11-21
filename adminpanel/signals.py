from django.db.models.signals import post_delete
from django.dispatch import receiver
from mainapp.models import ShippingAdress

@receiver(post_delete, sender=ShippingAdress)
def delete_order_when_address_deleted(sender, instance, **kwargs):
    """
    Deletes the associated Order when a ShippingAdress is deleted.
    """
    if instance.order:
        instance.order.delete()