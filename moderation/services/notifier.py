import os, json, requests
from django.utils.timezone import now
from moderation.models import NotificationLog

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify_if_inappropriate(request_obj, result_obj):
    if result_obj.classification in ("toxic", "spam", "harassment"):
        payload = {
            "text": f"⚠️ Moderation alert ({result_obj.classification}) for {request_obj.email} at {now().isoformat()}",
            "blocks":[{"type":"section","text":{"type":"mrkdwn",
                "text": f"*Classification:* {result_obj.classification}\n*Confidence:* {result_obj.confidence:.2f}\n*Reason:* {result_obj.reasoning[:180]}…"}}]
        }

        status = "failed"
        if SLACK_WEBHOOK_URL:
            try:
                r = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5)
                status = "sent" if r.ok else "failed"
            except Exception:
                status = "failed"

        NotificationLog.objects.create(request=request_obj, channel="slack", status=status)