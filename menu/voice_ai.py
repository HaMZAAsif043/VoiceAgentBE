"""
Voice AI endpoints for secure ElevenLabs integration.
Generates signed URLs to avoid exposing API keys on the frontend.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .services import ElevenLabsService
from .models import Call
import uuid


@csrf_exempt
@api_view(["POST"])
def get_signed_url(request):
    """
    Generate a signed URL for browser-based voice chat with ElevenLabs agent.

    This endpoint securely generates a signed URL on the backend, preventing
    exposure of the ELEVENLABS_API_KEY on the frontend.

    POST /voice-ai/signed-url/

    Request Body (optional):
    {
        "agent_id": "agent_...",  // optional override for testing/rotation
        "user_context": {
            "customer_name": "John Doe",
            "cart": [...],
            "any_custom_data": "..."
        }
    }

    Response (200 OK):
    {
        "success": true,
        "message": "Signed URL generated successfully",
        "data": {
            "signed_url": "wss://...",
            "conversation_id": "uuid-..."
        }
    }

    Response (500 Internal Server Error):
    {
        "success": false,
        "message": "Failed to generate signed URL: ...",
        "error": "..."
    }
    """
    # Extract optional user context from request
    user_context = request.data.get('user_context', {})
    requested_agent_id = request.data.get('agent_id')

    # Initialize ElevenLabs service
    elevenlabs_service = ElevenLabsService()

    # Generate signed URL from ElevenLabs API
    result = elevenlabs_service.get_signed_token_for_chat(
        user_context=user_context,
        agent_id=requested_agent_id
    )

    if not result['success']:
        http_status = result.get('status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "success": False,
            "message": result.get('user_message', f"Failed to generate signed URL: {result.get('error', 'Unknown error')}"),
            "error_code": result.get('error_code', 'unknown_error'),
            "error": result.get('error', 'Unknown error')
        }, status=http_status)

    # Generate a conversation ID for tracking
    conversation_id = str(uuid.uuid4())

    # Save call record to database for tracking
    call = Call.objects.create(
        phone_number='',  # Empty for browser calls
        call_type='browser',
        conversation_id=conversation_id,
        status='initiated',
        metadata=user_context
    )

    return Response({
        "success": True,
        "message": "Signed URL generated successfully",
        "data": {
            "signed_url": result['signed_url'],
            "conversation_id": conversation_id,
            "call_id": call.id
        }
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def health_check(request):
    """
    Health check endpoint to verify the voice AI service is operational.

    GET /voice-ai/health/

    Response (200 OK):
    {
        "success": true,
        "message": "Voice AI service is operational",
        "service": "ElevenLabs",
        "configured": true
    }
    """
    from django.conf import settings

    is_configured = bool(
        settings.ELEVENLABS_API_KEY and
        settings.ELEVENLABS_AGENT_ID
    )

    return Response({
        "success": True,
        "message": "Voice AI service is operational",
        "service": "ElevenLabs",
        "configured": is_configured
    }, status=status.HTTP_200_OK)
