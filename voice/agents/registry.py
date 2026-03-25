# voice/agents/registry.py
# Central registry of all voice agents.
# Each entry defines the agent's config — system prompt, tools, greeting, voices, languages.

from pathlib import Path
from . import healthcare, restaurant

# Available Gemini voices
ALL_VOICES = ["Aoede", "Puck", "Charon", "Kore", "Fenrir", "Leda"]
FEMALE_VOICES = ["Aoede", "Kore", "Leda"]       # warm female voices
MALE_VOICES   = ["Puck", "Charon", "Fenrir"]     # male voices

SUPPORTED_LANGUAGES = [
    {"code": "ur-PK", "label": "Urdu"},
    {"code": "en-US", "label": "English"},
]

# ---------------------------------------------------------------------------
# Registry: agent_id → config dict
# ---------------------------------------------------------------------------
AGENTS = {
    "healthcare": {
        "id": "healthcare",
        "name": "Healthcare Appointment",
        "description": "Book medical appointments with Sara, your scheduling assistant.",
        "icon": "🏥",
        "default_voice": "Aoede",
        "default_language": "ur-PK",
        "voices": FEMALE_VOICES,
        "languages": SUPPORTED_LANGUAGES,
        "greeting_path": healthcare.GREETING_PATH,
        "greeting_prompt": healthcare.GREETING_PROMPT,
        "build_system_prompt": healthcare.build_system_prompt,
        "tools": None,          # populated lazily per-language in get_agent_tools()
        "tools_fn": lambda: healthcare.TOOLS,
        "execute_tool": healthcare.execute_tool,
        # Google Calendar — read from env at runtime
        "calendar_creds_env": "HEALTHCARE_CALENDAR_CREDS",
        "calendar_id_env":    "HEALTHCARE_CALENDAR_ID",
    },
    "restaurant": {
        "id": "restaurant",
        "name": "Restaurant Booking",
        "description": "Reserve a table with Zara, your dining reservation assistant.",
        "icon": "🍽️",
        "default_voice": "Puck",
        "default_language": "ur-PK",
        "voices": ALL_VOICES,
        "languages": SUPPORTED_LANGUAGES,
        "greeting_path": restaurant.GREETING_PATH,
        "greeting_prompt": restaurant.GREETING_PROMPT,
        "build_system_prompt": restaurant.build_system_prompt,
        "tools_fn": lambda: restaurant.TOOLS,
        "execute_tool": restaurant.execute_tool,
        # Google Calendar — read from env at runtime
        "calendar_creds_env": "RESTAURANT_CALENDAR_CREDS",
        "calendar_id_env":    "RESTAURANT_CALENDAR_ID",
    },
}


def get_agent(agent_id: str) -> dict | None:
    """Return the agent config dict, or None if not found."""
    return AGENTS.get(agent_id)


def list_agents_public() -> list:
    """Return a list of public-facing agent info (for the /voice/agents/ endpoint)."""
    return [
        {
            "id": cfg["id"],
            "name": cfg["name"],
            "description": cfg["description"],
            "icon": cfg["icon"],
            "default_voice": cfg["default_voice"],
            "default_language": cfg["default_language"],
            "voices": cfg["voices"],
            "languages": cfg["languages"],
        }
        for cfg in AGENTS.values()
    ]
