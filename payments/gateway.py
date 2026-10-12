import os

class GatewayUnavailable(Exception): pass

def client():
    key_id = os.environ.get("RAZORPAY_KEY_ID", "")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
    if not key_id or not key_secret:
        raise GatewayUnavailable("Online payment is not configured. Choose Cash on Delivery or configure Razorpay test keys.")
    try:
        import razorpay
    except ImportError as exc:
        raise GatewayUnavailable("Install the optional Razorpay SDK with: pip install razorpay") from exc
    return razorpay.Client(auth=(key_id, key_secret)), key_id

def create_gateway_order(amount_rupees, receipt):
    api, key_id = client()
    result = api.order.create({"amount": int(amount_rupees * 100), "currency": "INR", "receipt": receipt, "payment_capture": 1})
    return result, key_id

def verify_signature(order_id, payment_id, signature):
    api, _ = client()
    api.utility.verify_payment_signature({"razorpay_order_id": order_id, "razorpay_payment_id": payment_id, "razorpay_signature": signature})
