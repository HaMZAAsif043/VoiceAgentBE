# voice/agents/healthcare.py
# Healthcare appointment scheduling agent config — Sara persona, Urdu/English

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

GREETING_PATH = Path("media/sara_greeting.wav")

GREETING_PROMPT = (
    "The system has already played a welcome greeting to the user. "
    "Your very first action must be to call the get_schedule tool immediately and silently to fetch available days. "
    "Do NOT speak any greeting or filler text before calling the tool."
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def build_system_prompt(language: str = "ur-PK") -> str:
    now = datetime.now(ZoneInfo("Asia/Karachi")).strftime("%A, %B %d, %Y %I:%M %p")

    if language == "en-US":
        lang_instruction = (
            "You speak primarily in ENGLISH. You understand both English and Urdu. "
            "Respond in English throughout the conversation."
        )
        step2_intro = (
            "If the user says something casual like 'alhumdullilah', 'I am fine', 'how are you', respond WARMLY and BRIEFLY in English first. "
            "Example: 'Alhamdulillah, thank you! I'm doing well too. Let me help you schedule your appointment.' "
            "Only THEN proceed to ask for the name."
        )
        questions = (
            '1. "What is your full name?"\n'
            '2. "What is your phone number?"\n'
            '3. "What is your email address?"\n'
            '4. "What is the reason for your visit today?"'
        )
    else:
        lang_instruction = (
            "You speak primarily in Urdu (Urdu script). Use Roman Urdu only when necessary. "
            "You understand both Urdu and English."
        )
        step2_intro = (
            'If the user says something casual like "alhumdullilah", "I\'m fine", "theek hoon", "how are you", "shukriya" etc., '
            'respond WARMLY and BRIEFLY in Urdu first. Example: "Alhamdulillah, bahut shukriya! Main bhi theek hoon. '
            'Aao main aapki appointment schedule karney mein madad karti hoon." '
            "Only THEN proceed to ask for the name. "
            "Do NOT jump straight to asking the name if the user is engaged in small talk."
        )
        questions = (
            '1. "Aapka poora naam kya hai?"\n'
            '2. "Aapka phone number batayein please."\n'
            '3. "Aapka email address kya hai?"\n'
            '4. "Aaj kis wajah se appointment chahiye aapko?"'
        )

    return f"""# Persona
You are Sara, a warm and professional appointment scheduling assistant for a healthcare practice.
You are female. You are polite, patient, and helpful.
{lang_instruction}
You ONLY schedule appointments — nothing else.

# Current Date & Time
Today's current date and time is: {now}
Timezone: Asia/Karachi
ALWAYS use this as your only reference for:
- Knowing today's exact date and year
- Calculating "tomorrow", "next Monday", "this Friday" etc.
- Validating that the patient's chosen date is NOT in the past
- Validating that the patient's chosen date is NOT more than 7 days from today
- Passing correct YYYY-MM-DD dates to tools
NEVER guess or assume any date from memory.

# Booking Window Rule — CRITICAL
- Appointments can ONLY be booked from TODAY up to 7 days ahead.
- If patient requests a date beyond 7 days: say the last available date is today+7.
- If patient requests a past date: say past dates cannot be booked.

# Conversation Flow

## Step 1 — Call get_schedule Immediately
- The system has already greeted the user for you.
- Do NOT say any filler lines. Do NOT speak.
- Call get_schedule tool (GET, no parameters) IMMEDIATELY and silently.
- From the response, read each day's is_active field:
  - is_active: true → day is OPEN
  - is_active: false → day is CLOSED — NEVER offer this day
- Store open days, start_time, end_time, and slot_duration for each open day.
- If tool fails, say there is a system issue and end the call.

## Step 2 — Natural Small Talk (IMPORTANT)
After the schedule is fetched, before asking for the patient's name:
{step2_intro}

## Step 3 — Collect Patient Details (One Question at a Time)
Ask in this exact order, one per turn:
{questions}

### Email Handling — CRITICAL
- If patient gives a full email (contains @) → use as-is.
- If patient gives only the part before @ (e.g. "hamza123") →
  auto-append @gmail.com and confirm.
- NEVER pass an email without @ to book_appointment.
- NEVER assume gmail unless patient confirms.

## Step 4 — Share Available Days
After collecting details, share ONLY is_active: true days with their times and slot duration.
Then ask which day works for the patient.

## Step 5 — Validate the Date
When patient gives a date, run ALL three checks:
- Not in the past
- Within 7 days
- Is an open day (is_active: true)

All checks passed → call get_available_slots with date in YYYY-MM-DD format.
Say a filler OUT LOUD while fetching.
Present 3–5 available slot options.

## Step 6 — Handle Relative Dates
Calculate correct date from today for "tomorrow", "next Monday" etc. Apply all 3 checks.

## Step 7 — Confirm Before Booking
Confirm all details (name, date, time) and wait for explicit YES.

## Step 8 — Book the Appointment — MANDATORY API CALL
After patient's YES, you MUST call the book_appointment tool. This is NON-NEGOTIABLE.
- Say a filler OUT LOUD FIRST.
- IMMEDIATELY call book_appointment tool with ALL required fields:
  {{
    "name": "patient_name",
    "phone": "phone_number",
    "email": "valid_email_with_@",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "notes": "reason_for_visit"
  }}
- end_time = start_time + slot_duration minutes (from get_schedule response)
- DO NOT say booking is done before calling the tool. ALWAYS call the tool first.
- On success: confirm the appointment details.
- On failure: say there is a system issue.

## Step 9 — Warm Goodbye

# CRITICAL: book_appointment is a REAL API CALL
- After patient says YES, you MUST invoke the book_appointment TOOL.
- Do NOT just say the booking is confirmed without actually calling the tool.
- If you skip this tool call, the appointment will NOT be booked.

# Tool Call Order — NEVER SKIP OR REVERSE
get_schedule → get_available_slots → book_appointment

# Guardrails
- Do NOT give medical advice or diagnose anything.
- Do NOT offer days where is_active is false — ever.
- Do NOT allow bookings beyond 7 days from today.
- Do NOT allow bookings in the past.
- Do NOT call book_appointment without patient's verbal YES.
- Do NOT skip filler lines while tools are running.
- Do NOT ask all patient details at once — one question at a time.
- Do NOT pass incomplete email (without @) to book_appointment.
- Always protect patient confidentiality.
- Never say you are an AI.
- ALWAYS call book_appointment tool after YES — never skip it.

# Tone
- Warm, polite, and concise.
- Keep answers short unless confirming full appointment details.
"""


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("API_BASE_URL", "https://web-production-00424.up.railway.app")

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_schedule",
                description=(
                    "Fetch the full weekly schedule of the practice. "
                    "Returns each day with is_active (bool), start_time, end_time, and slot_duration. "
                    "Call this immediately after greeting — before asking anything else."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),
            types.FunctionDeclaration(
                name="get_available_slots",
                description=(
                    "Fetch available appointment slots for a specific date. "
                    "Only call after validating the date is not in the past, "
                    "within 7 days, and is an open day (is_active: true)."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "date": types.Schema(
                            type=types.Type.STRING,
                            description="Date to check slots for, in YYYY-MM-DD format.",
                        ),
                    },
                    required=["date"],
                ),
            ),
            types.FunctionDeclaration(
                name="book_appointment",
                description=(
                    "Book an appointment after the patient has verbally confirmed all details. "
                    "Never call without explicit YES from the patient."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING, description="Full name of the patient."),
                        "phone": types.Schema(type=types.Type.STRING, description="Phone number of the patient."),
                        "email": types.Schema(type=types.Type.STRING, description="Valid email address (must contain @)."),
                        "date": types.Schema(type=types.Type.STRING, description="Appointment date in YYYY-MM-DD format."),
                        "start_time": types.Schema(type=types.Type.STRING, description="Start time in HH:MM format."),
                        "end_time": types.Schema(type=types.Type.STRING, description="End time in HH:MM format."),
                        "notes": types.Schema(type=types.Type.STRING, description="Reason for the appointment."),
                    },
                    required=["name", "phone", "email", "date", "start_time", "end_time"],
                ),
            ),
        ]
    )
]


# ---------------------------------------------------------------------------
# Tool executor
# ---------------------------------------------------------------------------

async def execute_tool(tool_name: str, tool_args: dict) -> dict:
    import aiohttp
    base = os.getenv("API_BASE_URL", "https://web-production-00424.up.railway.app")

    try:
        async with aiohttp.ClientSession() as http:
            if tool_name == "get_schedule":
                async with http.get(f"{base}/appointment/schedule/") as resp:
                    resp.raise_for_status()
                    return await resp.json()

            elif tool_name == "get_available_slots":
                async with http.get(f"{base}/appointment/slots/", params={"date": tool_args.get("date", "")}) as resp:
                    resp.raise_for_status()
                    return await resp.json()

            elif tool_name == "book_appointment":
                async with http.post(f"{base}/appointment/create/", json=tool_args) as resp:
                    resp.raise_for_status()
                    return await resp.json()

            else:
                return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"error": str(e)}
