# voice/consumers_browser.py
#
# Browser WebSocket variant — raw PCM16 in/out, no mulaw conversion.
# Inherits all Gemini Live session logic from VoiceAgentConsumer.

from .consumers1 import VoiceAgentConsumer, GREETING_PATH, MIC_RATE, OUT_RATE, _save_wav
from google.genai import types
from websockets.exceptions import ConnectionClosed
import asyncio
import logging

logger = logging.getLogger(__name__)

BROWSER_PCM_CHUNK = 4800  # ~100ms at 24kHz PCM16

class BrowserVoiceConsumer(VoiceAgentConsumer):

    # ------------------------------------------------------------------
    # Override: receive raw PCM16 from browser, no mulaw decode
    # ------------------------------------------------------------------

    async def receive(self, bytes_data=None, text_data=None):
        if self._disconnecting or not bytes_data:
            return
        if not self._session_ready.is_set():
            return

        session = self.gemini_session
        if session is None:
            self._clear_session_state()
            return

        # Browser sends raw PCM16 16kHz — forward directly
        try:
            await session.send_realtime_input(
                audio=types.Blob(
                    data=bytes_data,
                    mime_type=f"audio/pcm;rate={MIC_RATE}",
                )
            )
        except ConnectionClosed as exc:
            logger.info("Gemini session closed while forwarding browser audio: %s", exc)
            self._clear_session_state()

    # ------------------------------------------------------------------
    # Override: send raw PCM16 to browser, no mulaw encode
    # ------------------------------------------------------------------

    async def _stream_pcm_to_sip(self, pcm_24k: bytes):
        """Stream cached greeting PCM directly to browser in chunks."""
        for i in range(0, len(pcm_24k), BROWSER_PCM_CHUNK):
            await self.send(bytes_data=pcm_24k[i : i + BROWSER_PCM_CHUNK])
            await asyncio.sleep(0.1)

    async def _receive_loop(self, session):
        """
        Same as parent but sends raw PCM16 instead of mulaw to the client.
        """
        greeting_buffer = bytearray()

        try:
            async for response in session.receive():
                sc = getattr(response, "server_content", None)
                if sc is None:
                    continue

                if getattr(sc, "input_transcription", None):
                    t = sc.input_transcription
                    if hasattr(t, "text") and t.text:
                        logger.info(f"[You] {t.text}")

                if getattr(sc, "model_turn", None):
                    for part in sc.model_turn.parts:
                        inline = getattr(part, "inline_data", None)
                        if inline and inline.data:
                            if self._save_as_greeting:
                                greeting_buffer.extend(inline.data)

                            # Raw PCM16 24kHz → browser handles it natively
                            await self.send(bytes_data=inline.data)

                if getattr(sc, "turn_complete", False):
                    if self._save_as_greeting and greeting_buffer:
                        _save_wav(bytes(greeting_buffer), GREETING_PATH, OUT_RATE)
                        logger.info(f"Greeting saved to {GREETING_PATH}")
                        self._save_as_greeting = False
                        greeting_buffer.clear()

        except ConnectionClosed as exc:
            logger.info("Browser receive loop closed: %s", exc)