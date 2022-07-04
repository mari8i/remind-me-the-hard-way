from __future__ import print_function

import datetime
import logging
import os.path
import pickle
import time
import webbrowser
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TIME_ZONE = "Europe/Rome"

REMIND_ME_THE_HARD_WAY_BEFORE_SECONDS = 30
LOOP_SLEEP_TIME_SECONDS = 10


# If modifying these scopes, delete the file token.pickle.
CALENDAR_ID = "alessandro.mariotti@zupit.it"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_events(start_time: datetime.datetime, end_time: datetime.datetime):
    credentials = get_credentials()

    service = build("calendar", "v3", credentials=credentials)

    results = []
    events = service.events()
    request = events.list(
        calendarId=CALENDAR_ID,
        maxResults=100,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    )
    while request is not None:
        page = request.execute()
        results += page.get("items", [])
        request = events.list_next(request, page)

    return results


def get_next_events(start_time: datetime.datetime, end_time: datetime.datetime, max_results=10):
    credentials = get_credentials()
    service = build("calendar", "v3", credentials=credentials)

    events = service.events()
    request = events.list(
        calendarId=CALENDAR_ID,
        maxResults=max_results,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    )

    page = request.execute()
    return page.get("items", [])


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


def get_now():
    return datetime.datetime.now(ZoneInfo(key=TIME_ZONE))


def get_today_start_end_time():
    now = get_now()
    start_time = now - datetime.timedelta(seconds=REMIND_ME_THE_HARD_WAY_BEFORE_SECONDS)
    end_time = now.replace(hour=23, minute=59, second=59, microsecond=999)

    return start_time, end_time


def register_browser():
    webbrowser.register(
        "chrome", None, webbrowser.BackgroundBrowser("/usr/bin/google-chrome-stable")
    )


def get_event_start_time(event):
    start_date_str = event["start"].get("dateTime", event["start"].get("date"))
    # return datetime.datetime.strptime(start_date_str, "yyyy-mm-ddThh:MM:ssZ")
    return datetime.datetime.fromisoformat(start_date_str)


def get_event_name(event):
    return event["summary"]


def get_event_conference_url(event):
    if "conferenceData" in event:
        conference_url = next(
            filter(
                lambda entry_point: entry_point["entryPointType"] == "video",
                event["conferenceData"]["entryPoints"],
            )
        )
        return conference_url["uri"]
    return None


def find_closest_conference():
    start_time, end_time = get_today_start_end_time()
    events = get_events(start_time, end_time)

    for event in events:
        conference_url = get_event_conference_url(event)

        if conference_url:
            return event, conference_url

    return None


def main():
    logger = logging.getLogger("remind-me-the-hard-way")
    logger.setLevel(level=logging.INFO)
    logger.addHandler(logging.StreamHandler())

    logger.info("Setting up the browser")

    register_browser()

    logger.info("Starting main loop")

    handled_events = set()
    while True:
        logger.info("Finding closest conference")

        closest_conference = find_closest_conference()
        if not closest_conference:
            logger.info("There are no events scheduled at the moment..")
        else:
            event, conference_url = closest_conference
            event_name = get_event_name(event)
            event_start_time = get_event_start_time(event)

            logger.info(f"Closest conference is {event_name} starting at {event_start_time}")

            if event["id"] not in handled_events and conference_url is not None:
                logger.info(f"Event {event_name} has not been handled, starts at {event_start_time}")

                now = get_now()
                if now >= (event_start_time - datetime.timedelta(seconds=REMIND_ME_THE_HARD_WAY_BEFORE_SECONDS)):
                    logger.info(f"Opening event {event_name} in browser")
                    webbrowser.get("chrome").open(conference_url)
                    handled_events.add(event["id"])

        time.sleep(LOOP_SLEEP_TIME_SECONDS)


if __name__ == "__main__":
    main()
