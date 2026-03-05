import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsManager:
    """
    Utility to manage ElevenLabs Conversational AI agents programmatically.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ELEVEN_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY not found. Please set it in your .env file.")
        
        self.client = ElevenLabs(api_key=self.api_key)

    def get_agent(self, agent_id):
        """Fetch details of a specific agent."""
        return self.client.conversational_ai.get_agent(agent_id=agent_id)

    def update_agent(self, agent_id, name=None, conversation_config=None, platform_settings=None):
        """
        Update an agent's configuration.
        
        :param agent_id: The ID of the agent to update.
        :param name: Optional new name for the agent.
        :param conversation_config: dict containing system_prompt, model, tools, etc.
        :param platform_settings: dict containing endpoint/webhook settings.
        """
        update_data = {}
        if name:
            update_data['name'] = name
        if conversation_config:
            update_data['conversation_config'] = conversation_config
        if platform_settings:
            update_data['platform_settings'] = platform_settings

        return self.client.conversational_ai.update_agent(
            agent_id=agent_id,
            **update_data
        )

    def update_prompt(self, agent_id, system_prompt):
        """Helper to specifically update the system prompt (agent's personality)"""
        return self.client.conversational_ai.update_agent(
            agent_id=agent_id,
            conversation_config={
                "agent": {
                    "prompt": {
                        "prompt": system_prompt
                    }
                }
            }
        )

# Example Usage:
# manager = ElevenLabsManager()
# manager.update_prompt("YOUR_AGENT_ID", "You are a helpful assistant for KFC.")
