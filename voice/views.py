# voice/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .agents.registry import list_agents_public


# ---------------------------------------------------------------------------
# Twilio webhook views (kept for URL compatibility)
# ---------------------------------------------------------------------------

@csrf_exempt
def incoming_call(request):
    """Twilio incoming call webhook — returns TwiML to connect to media stream."""
    tunnel_url = "8rc8g56h-8000.asse.devtunnels.ms"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{tunnel_url}/ws/voice/stream/" />
  </Connect>
</Response>"""
    return HttpResponse(twiml, content_type="text/xml")


@csrf_exempt
def call_status(request):
    """Twilio call status callback — logs status updates."""
    return HttpResponse("OK", status=200)


# ---------------------------------------------------------------------------
# Voice agent list API
# ---------------------------------------------------------------------------

@api_view(["GET"])
def agents_list(request):
    """Return public list of all available voice agents with their config."""
    return Response(list_agents_public())
