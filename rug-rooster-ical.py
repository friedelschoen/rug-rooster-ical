#!/usr/bin/env python3

import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, parse_qs
import requests
from ics import Calendar, Event


ROOSTER_URL = os.getenv("ROOSTER_URL", "https://rooster.rug.nl/maat/api/2026-2027/schedule")
TIMEZONE = ZoneInfo(os.getenv("ROOSTER_Z", "Europe/Amsterdam"))


def parse_datetime(value):
    # API formaat: [2026, 9, 2, 13, 0]
    return datetime(*value, tzinfo=TIMEZONE)


def event_description(item):
    lines = []

    courses = item.get("courseOfferings", [])
    if courses:
        lines.append("Courses:")
        for course in courses:
            lines.append(
                f"- {course['displayNameEn']} ({course['courseCode']})"
            )

    activity_type = item.get("activityType")
    if activity_type:
        lines.append("")
        lines.append(f"Type: {activity_type['displayNameEn']}")

    description = item.get("description")
    if description:
        lines.append(f"Activity: {description}")

    groups = item.get("studentGroups", [])
    if groups:
        lines.append("")
        lines.append("Student groups:")
        for group in groups:
            lines.append(f"- {group['displayNameEn']}")

    rooms = item.get("rooms", [])
    if rooms:
        lines.append("")
        lines.append("Rooms:")
        for room in rooms:
            lines.append(f"- {room['code']} - {room['displayNameEn']}: {room['urlMap']}")

    staff = item.get("staff", [])
    if staff:
        lines.append("")
        lines.append("Staff:")
        for person in staff:
            lines.append(f"- {person['displayNameEn']}")

    comment = item.get("comment")
    if comment:
        lines.append("")
        lines.append(f"Comment: {comment}")

    if item.get("preliminary"):
        lines.append("")
        lines.append("PRELIMINARY")

    if item.get("changed"):
        lines.append("")
        lines.append("CHANGED")

    return "\n".join(lines)


def event_name(item):
    courses = item.get("courseOfferings", [])
    activity = item.get("activityType")

    if courses:
        name = courses[0]["displayNameEn"]
    else:
        name = "RUG"

    if activity:
        name += f" — {activity['displayNameEn']}"

    return name


def event_location(item):
    rooms = item.get("rooms", [])
    return ", ".join(room["code"] + " " + room["displayNameEn"] for room in rooms)


def fetch_calendar(courses):
    response = requests.post(
        ROOSTER_URL,
        json={
            "objects": [],
            "courseOfferingCodes": courses,
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()

    calendar = Calendar()
    calendar.creator = "RUG calendar"

    for item in data["results"]:
        event = Event(
            uid=f"{item['id']}@rooster.rug.nl",
            name=event_name(item),
            begin=parse_datetime(item["start"]),
            end=parse_datetime(item["end"]),
            location=event_location(item),
            description=event_description(item),
        )

        calendar.events.add(event)

    return str(calendar)


class CalendarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path not in ("/", "/rooster.ics", "/calendar.ics"):
            self.send_error(404)
            return

        query = parse_qs(url.query)

        course_offering = query.get("courseOffering")
        if not course_offering:
            self.send_error(400, "Missing courseOffering")
            return

        courses = [
            course.strip()
            for course in course_offering[0].split(",")
            if course.strip()
        ]

        if not courses:
            self.send_error(400, "Empty courseOffering")
            return

        try:
            calendar = fetch_calendar(courses)
            body = calendar.encode("utf-8")
        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError,
        ) as exc:
            self.send_error(502, f"Unable to fetch RUG schedule: {exc}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/calendar; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 6565), CalendarHandler)
    print("Serving calendar on http://127.0.0.1:6565/calendar.ics")
    server.serve_forever()
