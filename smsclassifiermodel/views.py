from django.http import HttpResponse, HttpResponseBadRequest

from .classifier import classify


def home(request):
    return HttpResponse("<h1>Oh Hello There</h1>")


def classify_text(request):
    """GET /classify/?string=<sms text>  ->  "normal", "promo" or "spam" (plain text)."""
    text = request.GET.get("string")
    if not text:
        return HttpResponseBadRequest("Pass the SMS text as ?string=...")
    return HttpResponse(classify(text), content_type="text/plain")
