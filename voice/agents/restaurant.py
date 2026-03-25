# voice/agents/restaurant.py
# Restaurant table booking agent — for KFC / restaurant use case

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from google.genai import types
except ImportError:
    raise ImportError("pip install google-genai")

# ---------------------------------------------------------------------------
# Greeting
# ---------------------------------------------------------------------------

GREETING_PATH = Path("media/restaurant_greeting.wav")

GREETING_PROMPT = (
    "The system has already played a welcome greeting to the customer. "
    "Your very first action must be to call the get_restaurant_schedule tool immediately and silently to fetch available days. "
    "Do NOT speak any greeting or filler text before calling the tool."
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def build_system_prompt(language: str = "ur-PK") -> str:
    now = datetime.now(ZoneInfo("Asia/Karachi")).strftime("%A, %B %d, %Y %I:%M %p")

    if language == "en-US":
        lang_instruction = "You speak primarily in ENGLISH. You understand both English and Urdu."
        small_talk = (
            "If the customer says something casual like 'I'm fine', 'alhumdullilah', respond WARMLY and BRIEFLY in English. "
            "Example: 'Great to hear! Let me help you book a table.' Only THEN proceed to ask for their name."
        )
        questions = (
            '1. "What is your full name?"\n'
            '2. "What is your phone number?"\n'
            '3. "How many people will be dining?" (minimum 1, maximum 10)\n'
            '4. "Do you have any special requests or dietary requirements?"'
        )
    else:
        lang_instruction = (
            "You speak primarily in Urdu (Urdu script). Use Roman Urdu only when necessary. "
            "You understand both Urdu and English."
        )
        small_talk = (
            'If the customer says something casual like "alhumdullilah", "I\'m fine", "theek hoon" etc., '
            'respond WARMLY and BRIEFLY in Urdu first. Example: "Bahut shukriya! Main aapki reservation mein madad karta/karti hoon." '
            "Only THEN ask for their name."
        )
        questions = (
            '1. "Aapka poora naam kya hai?"\n'
            '2. "Aapka phone number batayein please."\n'
            '3. "Kitne log dining mein shamil honge?" (minimum 1, maximum 10)\n'
            '4. "Koi khaas request ya dietary requirement hai?"'
        )

    return f"""# Persona
You are Zara, a warm and professional table reservation assistant for our restaurant.
You are polite, friendly, and efficient.
{lang_instruction}
You ONLY handle table reservations — nothing else.

# Current Date & Time
Today's current date and time is: {now}
Timezone: Asia/Karachi
ALWAYS use this as your reference for:
- Knowing today's exact date and year
- Calculating "tomorrow", "next Monday" etc.
- Validating that the chosen date is NOT in the past
- Validating that the chosen date is NOT more than 14 days from today
- Passing correct YYYY-MM-DD dates to tools

# Booking Window Rule — CRITICAL
- Table reservations can ONLY be booked from TODAY up to 14 days ahead.
- If customer requests a date beyond 14 days: say we only accept reservations 14 days in advance.
- If customer requests a past date: say past dates cannot be booked.

# Conversation Flow

## Step 1 — Call get_restaurant_schedule Immediately
- The system has already greeted the customer.
- Do NOT say any filler lines yet. Do NOT speak.
- Call get_restaurant_schedule tool IMMEDIATELY and silently.
- From the response, read each day's is_active field:
  - is_active: true → restaurant is OPEN that day
  - is_active: false → restaurant is CLOSED — NEVER offer this day
- Note open days, opening_time, closing_time, and reservation_duration.

## Step 2 — Natural Small Talk (IMPORTANT)
{small_talk}

## Step 3 — Collect Customer Details (One Question at a Time)
Ask in this exact order, one per turn:
{questions}

## Step 4 — Share Available Days
After collecting details, tell the customer which days the restaurant is open.
Say opening and closing times. Then ask which day they'd like to reserve.

## Step 5 — Validate the Date
When customer gives a date, check:
1. Not in the past
2. Within 14 days
3. Restaurant is open (is_active: true) on that day

All checks passed → call get_available_tables with date and party_size.
Say a filler OUT LOUD while fetching ("Ek lamha..." or "One moment...").
Present available time slots.

## Step 6 — Handle Relative Dates
Calculate correct date from today. Apply all 3 checks. Confirm with customer.

## Step 7 — Confirm Before Booking
Confirm: name, date, time, party size, special requests. Wait for explicit YES.

## Step 8 — Book the Table — MANDATORY API CALL
After customer's YES, you MUST call the book_table tool. This is NON-NEGOTIABLE.
- Say a filler OUT LOUD FIRST.
- IMMEDIATELY call book_table tool with ALL required fields:
  {{
    "name": "customer_name",
    "phone": "phone_number",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "party_size": <number>,
    "notes": "special_requests"
  }}
- DO NOT say booking is confirmed before calling the tool.
- On success: confirm reservation details to the customer.
- On failure: apologize and ask them to try again.

## Step 9 — Warm Goodbye

# CRITICAL: book_table is a REAL API CALL
- After customer says YES, you MUST invoke the book_table TOOL.
- Without calling it, no reservation is saved.

# Tool Call Order
get_restaurant_schedule → get_available_tables → book_table

# Guardrails
- Do NOT take food orders — only reservations.
- Do NOT offer closed days.
- Do NOT book beyond 14 days from today.
- Do NOT book in the past.
- Do NOT call book_table without explicit YES.
- Ask details one at a time — never all at once.
- Never say you are an AI.
- ALWAYS call book_table after YES — never skip it.

# Tone
- Warm, welcoming, and concise.
- Keep responses short unless confirming full reservation details.
"""


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_restaurant_schedule",
                description=(
                    "Fetch the weekly opening schedule of the restaurant. "
                    "Returns each day with is_active, opening_time, closing_time, and reservation_duration. "
                    "Call this immediately after greeting."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),
            types.FunctionDeclaration(
                name="get_available_tables",
                description=(
                    "Fetch available table reservation slots for a specific date and party size."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "date": types.Schema(type=types.Type.STRING, description="Date in YYYY-MM-DD format."),
                        "party_size": types.Schema(type=types.Type.INTEGER, description="Number of people dining."),
                    },
                    required=["date", "party_size"],
                ),
            ),
            types.FunctionDeclaration(
                name="book_table",
                description=(
                    "Book a table reservation after the customer has verbally confirmed all details. "
                    "Never call without explicit YES from the customer."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING, description="Full name of the customer."),
                        "phone": types.Schema(type=types.Type.STRING, description="Phone number of the customer."),
                        "date": types.Schema(type=types.Type.STRING, description="Reservation date in YYYY-MM-DD format."),
                        "start_time": types.Schema(type=types.Type.STRING, description="Reservation start time in HH:MM format."),
                        "end_time": types.Schema(type=types.Type.STRING, description="Reservation end time in HH:MM format."),
                        "party_size": types.Schema(type=types.Type.INTEGER, description="Number of people dining."),
                        "notes": types.Schema(type=types.Type.STRING, description="Special requests or dietary notes."),
                    },
                    required=["name", "phone", "date", "start_time", "end_time", "party_size"],
                ),
            ),
        ]
    )
]


# ---------------------------------------------------------------------------
# Tool executor — reuses appointment API pattern for schedule/slots,
# adds restaurant-specific book_table endpoint
# ---------------------------------------------------------------------------

async def execute_tool(tool_name: str, tool_args: dict) -> dict:
    import aiohttp
    base = "http://127.0.0.1:8000"
    try:
        async with aiohttp.ClientSession() as http:
            if tool_name == "get_restaurant_schedule":
                # Reuse the appointment schedule API (same pattern, same DB)
                async with http.get(f"{base}/appointment/schedule/") as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    # Remap field names to restaurant terminology
                    if data.get("success") and data.get("data"):
                        for day in data["data"]:
                            day["opening_time"] = day.pop("start_time", day.get("opening_time"))
                            day["closing_time"] = day.pop("end_time", day.get("closing_time"))
                            day["reservation_duration"] = day.pop("slot_duration", day.get("reservation_duration"))
                    return data

            elif tool_name == "get_available_tables":
                params = {"date": tool_args.get("date", "")}
                party_size = tool_args.get("party_size", 1)
                async with http.get(f"{base}/appointment/slots/", params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    # Add party size context to the response
                    data["party_size"] = party_size
                    return data

            elif tool_name == "book_table":
                # Map restaurant fields to appointment API fields
                payload = {
                    "name": tool_args.get("name"),
                    "phone": tool_args.get("phone"),
                    "email": tool_args.get("email", f"{tool_args.get('phone', 'guest')}@restaurant.local"),
                    "date": tool_args.get("date"),
                    "start_time": tool_args.get("start_time"),
                    "end_time": tool_args.get("end_time"),
                    "notes": f"Party of {tool_args.get('party_size', 1)}. {tool_args.get('notes', '')}".strip(),
                }
                async with http.post(f"{base}/appointment/create/", json=payload) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    result["party_size"] = tool_args.get("party_size", 1)
                    return result

            else:
                return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"error": str(e)}
