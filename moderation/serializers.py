from rest_framework import serializers

class TextModerateIn(serializers.Serializer):
    email = serializers.EmailField()
    text = serializers.CharField(max_length=4000)

    def validate_text(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Text cannot be empty")
        
        return value

class ImageModerateIn(serializers.Serializer):
    email = serializers.EmailField()
    image = serializers.ImageField()  # multipart/form-data

    def validate_image(self, f):
        max_mb = 8
        if f.size and f.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"image larger than {max_mb}MB")

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if hasattr(f, "content_type") and f.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
        return f

class SummaryQuery(serializers.Serializer):
    user = serializers.EmailField()


class ModerateResponseOut(serializers.Serializer):
    request_id = serializers.IntegerField()
    classification = serializers.ChoiceField(choices=("toxic", "spam", "harassment", "safe"))

    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    reasoning = serializers.CharField(allow_blank=True)

class AnalyticsLabelCount(serializers.Serializer):
    classification = serializers.CharField()
    count = serializers.IntegerField(min_value=0)


class AnalyticsSummaryOut(serializers.Serializer):
    user = serializers.EmailField()
    total_items = serializers.IntegerField(min_value=0)
    by_label = AnalyticsLabelCount(many=True)
    last_24h = serializers.IntegerField(min_value=0)

class ErrorOut(serializers.Serializer):
    error = serializers.CharField()