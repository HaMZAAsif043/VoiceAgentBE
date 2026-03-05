# appointments/services/google_calendar.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
# Use absolute path relative to this file's location
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
CALENDAR_ID = 'hamza.asif0087@gmail.com'  # or 'primary'
TIMEZONE = 'Asia/Karachi'


def get_calendar_service():
    """Build and return Google Calendar service"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds)


def create_meeting(appointment):
    """
    Creates a Google Calendar event with Meet link
    from an Appointment instance
    """
    service = get_calendar_service()

    # Combine date + time into datetime
    start_dt = datetime.combine(appointment.date, appointment.start_time)
    end_dt   = datetime.combine(appointment.date, appointment.end_time)

    event = {
        'summary': f'Appointment - {appointment.name}',
        'description': appointment.notes or '',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        # 'attendees': [
        #     {'email': appointment.email},   # customer
        #     # {'email': 'your@email.com'},  # optionally add host
        # ],
        'conferenceData': {
            'createRequest': {
                'requestId': f'appt-{appointment.id}',  # unique per event
                'conferenceSolutionKey': {'type': 'eventHangout'},
            }
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},   # 1 hr before
                {'method': 'popup', 'minutes': 15},   # 15 min before
            ]
        }
    }

    result = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=0,  # ← change from 1 to 0
        sendUpdates='none',          # sends email invites to attendees
    ).execute()

    return {
        'event_id':  result.get('id'),
        'meet_link': result.get('conferenceData', {})
                           .get('entryPoints', [{}])[0]
                           .get('uri'),
        'calendar_link': result.get('htmlLink')
    }


def cancel_meeting(event_id):
    """Delete/cancel a calendar event"""
    service = get_calendar_service()
    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=event_id,
        sendUpdates='all'
    ).execute()