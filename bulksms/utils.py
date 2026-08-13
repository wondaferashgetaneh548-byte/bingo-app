import os
from django.conf import settings
from twilio.rest import Client

def send_bulk_sms(recipients, message_body):
    # Credentials-ቹን ከ ጽሁፍ (string) ወደ ጸዳ UTF-8 መቀየር
    account_sid = str(settings.TWILIO_ACCOUNT_SID).strip()
    auth_token = str(settings.TWILIO_AUTH_TOKEN).strip()
    from_number = str(settings.TWILIO_PHONE_NUMBER).strip()

    client = Client(account_sid, auth_token)
    results = []

    for number in recipients:
        try:
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=str(number).strip()
            )
            results.append({
                "number": number,
                "status": "success",
                "sid": message.sid
            })
        except Exception as e:
            results.append({
                "number": number,
                "status": "failed",
                "error": str(e)
            })

    return results