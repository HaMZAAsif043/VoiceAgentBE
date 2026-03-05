import hmac
import hashlib
import json
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os

from elevenlabs.client import ElevenLabs
from menu.models.Call import Call

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ElevenLabsWebhookView(APIView):
    """
    Webhook handler for ElevenLabs Conversational AI.
    Listens for 'post_call_transcription' events.
    """
    
    def post(self, request, *args, **kwargs):
        # 1. Get the signature from headers
        signature = request.headers.get('ElevenLabs-Signature')
        if not signature:
            logger.warning("Missing ElevenLabs-Signature header")
            return Response({"error": "Missing signature"}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Get the raw body and secret
        payload = request.body.decode('utf-8')
        secret = os.getenv('ELEVEN_LABS_WEBHOOK_SECRET')
        api_key = os.getenv('ELEVEN_LABS_API_KEY')
        
        if not secret:
            logger.error("ELEVEN_LABS_WEBHOOK_SECRET not set in environment")
            return Response({"error": "Configuration error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Verify signature using ElevenLabs SDK
        try:
            client = ElevenLabs(api_key=api_key)
            # This method parses the t=... v0=... format and validates the HMAC
            data = client.webhooks.construct_event(
                rawBody=payload,
                sig_header=signature,
                secret=secret
            )
        except Exception as e:
            logger.warning(f"Webhook Signature Verification Failed: {str(e)}")
            return Response({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. Process the validated payload
        try:
            event_type = data.get('type')

            
            if event_type == 'post_call_transcription':
                # 1. Extract Details from Payload
                conversation_data = data.get('data', {}) # Old SDK version might put it in 'data'
                if not conversation_data:
                    conversation_data = data # New SDK version might pass the whole payload
                
                conversation_id = conversation_data.get('conversation_id')
                transcript_data = conversation_data.get('transcript', [])
                analysis = conversation_data.get('analysis', {})
                metadata = conversation_data.get('metadata', {})
                
                # Format transcript for TextField
                formatted_transcript = ""
                for entry in transcript_data:
                    role = entry.get('role', 'unknown')
                    message = entry.get('message', '')
                    if message: # Skip entries with no message (like tool calls alone)
                        formatted_transcript += f"{role.capitalize()}: {message}\n"

                # 2. Map Payload to Call Model
                # Extracting specific fields from the provided JSON structure
                call_status = 'completed' if data.get('status') == 'done' else 'failed'
                if analysis.get('call_successful') == 'success':
                    call_status = 'completed'

                # duration_seconds mapping
                duration = metadata.get('call_duration_secs') or metadata.get('duration_seconds')

                # Find or create the Call record
                call_record, created = Call.objects.get_or_create(
                    conversation_id=conversation_id,
                    defaults={
                        'phone_number': metadata.get('phone_number') or 'unknown',
                        'call_type': 'browser' if conversation_data.get('conversation_initiation_source') == 'react_sdk' else 'outbound'
                    }
                )

                # Update the record with full details
                call_record.status = call_status
                call_record.transcript = formatted_transcript
                call_record.duration_seconds = duration
                
                # Store enrichment in metadata field
                enriched_metadata = {
                    'agent_name': data.get('agent_name'),
                    'call_successful': analysis.get('call_successful'),
                    'transcript_summary': analysis.get('transcript_summary'),
                    'call_summary_title': analysis.get('call_summary_title'),
                    'cost': metadata.get('cost'),
                    'language': metadata.get('main_language'),
                    'raw_payload': data # Store full response for safety
                }
                call_record.metadata = enriched_metadata
                call_record.save()
                
                logger.info(f"{'Created' if created else 'Updated'} call record for: {conversation_id}")
                return Response({"status": "success", "conversation_id": conversation_id}, status=status.HTTP_200_OK)
            
            else:
                logger.info(f"Ignored event type: {event_type}")
                return Response({"status": "ignored"}, status=status.HTTP_200_OK)


        except Exception as e:
            logger.error(f"Error processing ElevenLabs webhook: {str(e)}")
            return Response({"error": "Internal processing error"}, status=status.HTTP_400_BAD_REQUEST)

    def process_conversation(self, data):
        # Placeholder for custom logic (e.g., updating order status)
        pass
