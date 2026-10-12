from django.core.exceptions import ValidationError
from .models import Order

ALLOWED_TRANSITIONS = {
    Order.Status.PENDING: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
    Order.Status.CONFIRMED: {Order.Status.PREPARING, Order.Status.CANCELLED},
    Order.Status.PREPARING: {Order.Status.OUT_FOR_DELIVERY},
    Order.Status.OUT_FOR_DELIVERY: {Order.Status.DELIVERED},
    Order.Status.DELIVERED: set(), Order.Status.CANCELLED: set(),
}

def change_status(order, next_status):
    if next_status not in Order.Status.values or next_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise ValidationError("That order status transition is not permitted.")
    if next_status == Order.Status.CANCELLED and order.payment_status == Order.PaymentStatus.PAID:
        raise ValidationError("A paid order cannot be cancelled until the payment is refunded by an administrator.")
    order.status = next_status
    order.save(update_fields=["status", "updated_at"])
    return order
