import requests
import logging
from app.config import settings

# All Paystack API calls go to this base URL
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Logger for this module so errors are traceable in your logs
logger = logging.getLogger(__name__)

# Authorization header built once and reused in every request.
# The Secret Key tells Paystack this request is coming from our server.
HEADERS = {
    "Authorization": f"Bearer {settings.paystack_secret_key}",
    "Content-Type": "application/json",
}


def initialize_payment(email: str, amount_naira: float, order_id: int) -> dict:
    """
    Opens a payment session with Paystack and returns a payment URL
    that the frontend redirects the user to.

    Args:
        email        -- the customer's email address
        amount_naira -- total order amount in Naira (e.g. 5000.00)
        order_id     -- our internal Order ID stored in metadata so
                        Benedict's webhook can match the payment back
                        to the correct order

    Returns a dict with:
        status            -- True if Paystack accepted the request
        authorization_url -- the hosted payment page URL to redirect user to
        reference         -- unique reference string for this payment
        message           -- description from Paystack
    """
    # Paystack requires amounts in kobo (1 Naira = 100 kobo)
    amount_kobo = int(amount_naira * 100)

    payload = {
        "email": email,
        "amount": amount_kobo,
        "metadata": {
            # This order_id travels with the payment all the way to
            # the webhook so Benedict can identify which order was paid
            "order_id": order_id,
        },
        # After payment, Paystack redirects the user back to this URL.
        # Solex will build the /payment/callback page on the frontend.
        "callback_url": f"{settings.frontend_url}/payment/callback",
    }

    try:
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload,
            headers=HEADERS,
            timeout=10,  # fail fast if Paystack is unreachable
        )
        response.raise_for_status()  # raises exception on 4xx/5xx responses
        data = response.json()

        return {
            "status": data.get("status", False),
            "authorization_url": data["data"]["authorization_url"],
            "reference": data["data"]["reference"],
            "message": data.get("message", ""),
        }

    except requests.exceptions.Timeout:
        logger.error("Paystack initialize: request timed out")
        return {"status": False, "message": "Payment provider timed out. Please try again."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Paystack initialize error: {e}")
        return {"status": False, "message": "Could not connect to payment provider."}


def verify_payment(reference: str) -> dict:
    """
    Verifies a completed payment using its unique reference string.
    Called by Solex's verification endpoint after the user returns
    from Paystack's payment page.

    Args:
        reference -- the reference string from initialize_payment,
                     passed back by Paystack in the redirect URL

    Returns a dict with:
        status  -- True if Paystack responded successfully
        paid    -- True if the actual payment was successful
        amount  -- amount charged in Naira (converted back from kobo)
        email   -- customer email Paystack has on file
        message -- description from Paystack
    """
    try:
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        transaction = data.get("data", {})
        payment_status = transaction.get("status", "")

        return {
            "status": data.get("status", False),
            "paid": payment_status == "success",
            "amount": transaction.get("amount", 0) / 100,  # convert kobo back to Naira
            "email": transaction.get("customer", {}).get("email", ""),
            "message": data.get("message", ""),
        }

    except requests.exceptions.Timeout:
        logger.error(f"Paystack verify: timed out for reference {reference}")
        return {"status": False, "paid": False, "message": "Verification timed out."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Paystack verify error: {e}")
        return {"status": False, "paid": False, "message": "Verification failed."}