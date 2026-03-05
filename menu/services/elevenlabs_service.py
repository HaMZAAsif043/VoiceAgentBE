from elevenlabs.client import ElevenLabs
from django.conf import settings
import uuid


class ElevenLabsService:
    """Service class for interacting with ElevenLabs API"""

    def __init__(self):
        """Initialize ElevenLabs client with API key from settings"""
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.agent_id = settings.ELEVENLABS_AGENT_ID

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

    def get_signed_token_for_chat(self, user_context=None):
        """
        Generate a signed token for browser-based voice chat.

        Args:
            user_context (dict, optional): User context data for the session

        Returns:
            dict: Response containing signed URL or token
        """
        try:
            # Generate a signed token/URL for the ElevenLabs Web SDK
            # This allows the frontend to connect securely to the agent
            response = self.client.conversational_ai.conversations.get_signed_url(
                agent_id=self.agent_id
            )

            return {
                'success': True,
                'signed_url': response.signed_url,
                'agent_id': self.agent_id,
                'expires_at': getattr(response, 'expires_at', None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
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
