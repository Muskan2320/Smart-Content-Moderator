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
    image = serializers.ImageField(required=False)        # file upload
    image_url = serializers.URLField(required=False)      # remote URL

    def validate(self, attrs):
        if not attrs.get("image") and not attrs.get("image_url"):
            raise serializers.ValidationError({"image": "Provide either image or image_url."})
        return attrs

class SummaryQuery(serializers.Serializer):
    user = serializers.EmailField()


class ModerateResponseOut(serializers.Serializer):
    requeest_id = serializers.IntegerField()
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