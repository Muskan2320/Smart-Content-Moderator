from django.db import models

class ModerationRequest(models.Model):
    CONTENT_TEXT = "text"
    CONTENT_IMAGE = "image"
    CONTENT_TYPES = [(CONTENT_TEXT, "Text"), (CONTENT_IMAGE, "Image")]

    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    content_hash = models.CharField(max_length=128, db_index=True)

    email = models.EmailField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

class ModerationResult(models.Model):
    request = models.OneToOneField(ModerationRequest, on_delete=models.CASCADE, related_name="result")
    classification = models.CharField(max_length=32) # toxic|spam|harassment|safe

    confidence = models.FloatField()
    reasoning = models.TextField(blank=True)
    llm_response = models.JSONField()

class NotificationLog(models.Model):
    request = models.ForeignKey(ModerationRequest, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=20)

    status = models.CharField(max_length=20)
    sent_at = models.DateTimeField(auto_now_add=True)