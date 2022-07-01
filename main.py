from __future__ import print_function

import datetime
import os.path
import pickle
import webbrowser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

REMIND_ME_THE_HARD_WAY_BEFORE_SECONDS = 30

# If modifying these scopes, delete the file token.pickle.
CALENDAR_ID = "alessandro.mariotti@zupit.it"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_events(start_time: datetime.datetime, end_time: datetime.datetime):
    credentials = get_credentials()

    service = build("calendar", "v3", credentials=credentials)

    # Call the Calendar API. 'Z' indicates UTC time
    start_time_ = start_time.isoformat() + "Z"
    end_time_ = end_time.isoformat() + "Z"

    results = []
    events = service.events()
    request = events.list(
        calendarId=CALENDAR_ID,
        maxResults=100,
        timeMin=start_time_,
        timeMax=end_time_,
        singleEvents=True,
        orderBy="startTime",
    )
    while request is not None:
        page = request.execute()
        results += page.get("items", [])
        request = events.list_next(request, page)

    return results


def get_credentials():
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return credentials


def get_today_start_end_time():
    now = datetime.datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=59, second=59, microsecond=999)

    return start_time, end_time


def register_browser():
    webbrowser.register(
        "chrome", None, webbrowser.BackgroundBrowser("/usr/bin/google-chrome-stable")
    )


def main():
    register_browser()

    start_time, end_time = get_today_start_end_time()
    events = get_events(start_time, end_time)

    now = datetime.datetime.now()
    for event in events:
        event_start_time = event["start"].get("dateTime", event["start"].get("date"))

        if "conferenceData" in event:
            print(event["conferenceData"])
            google_meet_data = next(
                filter(
                    lambda entry_point: entry_point["entryPointType"] == "video",
                    event["conferenceData"]["entryPoints"],
                )
            )
            print(event_start_time, event["summary"], google_meet_data)

            webbrowser.get("chrome").open(google_meet_data["uri"])
            return


if __name__ == "__main__":
    main()
