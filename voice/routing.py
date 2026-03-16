"""WebSocket URL patterns for Twilio media streams."""
from django.urls import re_path

from . import consumers
from . import consumers1
from voice.consumers_browser import BrowserVoiceConsumer  # Browser FE (PCM16)

websocket_urlpatterns = [
    re_path(r"^ws/voice/stream/$", consumers.TwilioMediaConsumer.as_asgi()),
    re_path(r"^ws/voice/voice-agent/$", consumers1.VoiceAgentConsumer.as_asgi()),
    re_path(r"^ws/voice/voice-agent-browser/$", BrowserVoiceConsumer.as_asgi()),  # FE
]



