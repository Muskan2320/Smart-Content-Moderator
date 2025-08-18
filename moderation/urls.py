from django.urls import path
from .views import ModerateTextView, ModerateImageView, AnalyticsSummary

urlpatterns = [
    path("moderate/text", ModerateTextView.as_view(), name="moderate-text"),
    path("moderate/image", ModerateImageView.as_view(), name="moderate-image"),
    path("analytics/summary", AnalyticsSummary.as_view(), name="analytics-summary"),
]