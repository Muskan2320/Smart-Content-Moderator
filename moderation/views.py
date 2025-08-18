from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import mimetypes, requests
from rest_framework import status
from django.db.models import Count, Q
from django.utils.timezone import now
from django.shortcuts import render

from .serializers import ImageModerateIn, TextModerateIn, SummaryQuery, ModerateResponseOut, AnalyticsSummaryOut
from .models import ModerationRequest, ModerationResult
from .services.hashing import sha256_bytes
from .services.gemini import classify_text, classify_image_bytes
from .services.notifier import notify_if_inappropriate

class ModerateTextView(APIView):
    def post(self, request):
        s = TextModerateIn(data=request.data)
        s.is_valid(raise_exception=True)
        email, text = s.validated_data["email"], s.validated_data["text"]
        req = ModerationRequest.objects.create(
            content_type="text",
            content_hash=sha256_bytes(text.encode("utf-8")),
            email=email,
            status="pending",
        )
        try:
            data = classify_text(text)
            res = ModerationResult.objects.create(
                request=req,
                classification=data["classification"],
                confidence=data.get("confidence", 0.5),
                reasoning=data.get("reasoning",""),
                llm_response=data.get("_raw", {}),
            )
            req.status = "processed"
            req.save(update_fields=["status"])
            notify_if_inappropriate(req, res)
            
            payload = {
                "request_id": req.id,
                "classification": res.classification,
                "confidence": res.confidence,
                "reasoning": res.reasoning,
            }
            out = ModerateResponseOut(payload)
            
            return Response(out.data, status=status.HTTP_200_OK)
        except Exception as e:
            req.status = "failed"; req.save(update_fields=["status"])
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModerateImageView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]   # <-- important

    def post(self, request):
        s = ImageModerateIn(data=request.data)  # DRF pulls files automatically
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]

        if s.validated_data.get("image"):
            up = s.validated_data["image"]  # InMemoryUploadedFile
            up.seek(0)
            img_bytes = up.read()
            mime_type = getattr(up, "content_type", None) or mimetypes.guess_type(up.name)[0] or "application/octet-stream"
        else:
            url = s.validated_data["image_url"]
            r = requests.get(url, timeout=15, stream=True)
            r.raise_for_status()
            # (Optional) enforce max size
            MAX = 10 * 1024 * 1024
            img_bytes, total = bytearray(), 0
            for chunk in r.iter_content(8192):
                if chunk:
                    total += len(chunk)
                    if total > MAX:
                        return Response({"error": "Image too large"}, status=413)
                    img_bytes.extend(chunk)
            img_bytes = bytes(img_bytes)
            mime_type = r.headers.get("Content-Type", "application/octet-stream")

        req = ModerationRequest.objects.create(
            content_type="image",
            content_hash=sha256_bytes(img_bytes),
            email=email,
            status="pending",
        )

        try:
            data = classify_image_bytes(img_bytes, mime_type=mime_type)
            res = ModerationResult.objects.create(
                request=req,
                classification=data["classification"],
                confidence=data.get("confidence", 0.5),
                reasoning=data.get("reasoning",""),
                llm_response=data.get("_raw", {}),
            )
            req.status = "processed"; req.save(update_fields=["status"])
            notify_if_inappropriate(req, res)
            return Response({
                "request_id": req.id,
                "classification": res.classification,
                "confidence": res.confidence,
                "reasoning": res.reasoning
            }, status=status.HTTP_200_OK)
        except Exception as e:
            req.status = "failed"; req.save(update_fields=["status"])
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalyticsSummary(APIView):
    def get(self, request):
        s = SummaryQuery(data=request.query_params)
        s.is_valid(raise_exception=True)
        email = s.validated_data["user"]

        qs = ModerationResult.objects.filter(request__email=email)
        total = qs.count()
        by_label = list(qs.values("classification").annotate(count=Count("id")))
        last_24h = qs.filter(request__created_at__gte=now()-__import__("datetime").timedelta(hours=24)).count()

        payload = {
            "user": email,
            "total_items": total,
            "by_label": by_label,  # [{"classification": "...", "count": n}, ...]
            "last_24h": last_24h,
        }
        out = AnalyticsSummaryOut(payload)
        
        return Response(out.data, status=status.HTTP_200_OK)