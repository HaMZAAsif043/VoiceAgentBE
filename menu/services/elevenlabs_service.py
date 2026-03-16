from elevenlabs.client import ElevenLabs
from django.conf import settings
import uuid


class ElevenLabsService:
    """Service class for interacting with ElevenLabs API"""

    def __init__(self):
        """Initialize ElevenLabs client with API key from settings"""
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.agent_id = settings.ELEVENLABS_AGENT_ID

    @staticmethod
    def _build_error_details(exc, agent_id):
        message = str(exc)
        lowered = message.lower()

        if "document_not_found" in lowered or "not found" in lowered:
            return {
                'error_code': 'agent_not_found',
                'user_message': (
                    f"The configured ElevenLabs agent '{agent_id}' was not found. "
                    "Update AGENT_ID/ELEVENLABS_AGENT_ID to an existing agent ID."
                ),
                'status_code': 404,
                'error': message,
            }

        if "unauthorized" in lowered or "401" in lowered or "invalid api key" in lowered:
            return {
                'error_code': 'invalid_api_key',
                'user_message': 'ElevenLabs API key is invalid or missing.',
                'status_code': 401,
                'error': message,
            }

        return {
            'error_code': 'elevenlabs_error',
            'user_message': 'Failed to communicate with ElevenLabs.',
            'status_code': 500,
            'error': message,
        }

    def initiate_phone_call(self, phone_number, context_data=None):
        """
        Initiate an outbound phone call to a customer using ElevenLabs agent.

        Args:
            phone_number (str): Customer phone number (e.g., '+923001234567')
            context_data (dict, optional): Additional context for the conversation

        Returns:
            dict: Response containing conversation_id and status
        """
        try:
            # Prepare the request for ElevenLabs conversational AI
            # Note: Using the conversations API for phone calls
            response = self.client.conversational_ai.create_agent_call(
                agent_id=self.agent_id,
                phone_number=phone_number,
                metadata=context_data or {}
            )

            return {
                'success': True,
                'conversation_id': response.conversation_id,
                'status': response.status,
                'phone_number': phone_number
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'conversation_id': None,
                'status': 'failed'
            }

    def get_signed_token_for_chat(self, user_context=None, agent_id=None):
        """
        Generate a signed token for browser-based voice chat.

        Args:
            user_context (dict, optional): User context data for the session

        Returns:
            dict: Response containing signed URL or token
        """
        target_agent_id = agent_id or self.agent_id

        if not target_agent_id:
            return {
                'success': False,
                'error_code': 'missing_agent_id',
                'user_message': 'No ElevenLabs agent is configured. Set AGENT_ID or ELEVENLABS_AGENT_ID.',
                'error': 'Missing ElevenLabs agent ID',
                'status_code': 500,
                'signed_url': None,
            }

        try:
            # Generate a signed token/URL for the ElevenLabs Web SDK
            # This allows the frontend to connect securely to the agent
            response = self.client.conversational_ai.conversations.get_signed_url(
                agent_id=target_agent_id
            )

            return {
                'success': True,
                'signed_url': response.signed_url,
                'agent_id': target_agent_id,
                'expires_at': getattr(response, 'expires_at', None)
            }
        except Exception as e:
            error_details = self._build_error_details(e, target_agent_id)
            return {
                'success': False,
                'error_code': error_details['error_code'],
                'user_message': error_details['user_message'],
                'status_code': error_details['status_code'],
                'error': error_details['error'],
                'signed_url': None
            }

    def get_conversation_status(self, conversation_id):
        """
        Get the status of an ongoing or completed conversation.

        Args:
            conversation_id (str): Unique conversation identifier

        Returns:
            dict: Conversation status and details
        """
        try:
            response = self.client.conversational_ai.get_conversation(
                conversation_id=conversation_id
            )

            return {
                'success': True,
                'conversation_id': conversation_id,
                'status': response.status,
                'transcript': getattr(response, 'transcript', None),
                'duration_seconds': getattr(response, 'duration', None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'unknown'
            }
