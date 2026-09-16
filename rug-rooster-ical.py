#!/usr/bin/env python3

import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, parse_qs
import requests
import traceback
from ics import Calendar, Event


ROOSTER_URL = os.getenv("ROOSTER_URL", "https://rooster.rug.nl/maat/api/2026-2027/schedule/generate")
TIMEZONE = ZoneInfo(os.getenv("ROOSTER_Z", "Europe/Amsterdam"))

BUILDINGS = {
    '1111': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic building'),
    '1112': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic building'),
    '1113': ("Oude Kijk in Het Jatstraat 39, 9712 EB Groningen, Nederland", ''),
    '1114': ("Oude Kijk in 't Jatstraat 41/41a, 9712 EB Groningen, Nederland", ''),
    '1116': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic building'),
    '1117': ('Muurstraat 14, 9712 EN Groningen, Nederland', ''),
    '1121': ('Oude Boteringestraat 44, 9712 GL Groningen, Nederland', 'Administration building'),
    '1124': ('Oude Boteringestraat 38', ''),
    '1126': ('Oude Boteringestraat 34', ''),
    '1131': ('Oude Boteringestraat 52', ''),
    '1134': ('Broerstraat 9', ''),
    '1211': ('Broerstraat 4', ''),
    '1212': ('Poststraat 6', ''),
    '1213': ("Oude Kijk in 't Jatstraat 7a", ''),
    '1219': ("Oude Kijk in 't Jatstraat 7a", ''),
    '1215': ("Oude Kijk in 't Jatstraat 9", ''),
    '1217': ('Oude Boteringestraat 18', 'Röling building'),
    '1221': ('Oude Boteringestraat 24', 'Calmershuis'),
    '1311': ("Oude Kijk in 't Jatstraat 26", 'Harmoniecomplex'),
    '1312': ("Oude Kijk in 't Jatstraat 26", 'Harmoniecomplex'),
    '1313': ("Oude Kijk in 't Jatstraat 26", 'Harmoniecomplex'),
    '1314': ("Oude Kijk in 't Jatstraat 26", 'Harmoniecomplex'),
    '1315': ("Oude Kijk in 't Jatstraat 26", 'Harmoniecomplex'),
    '1321': ("Oude Kijk in 't Jatstraat 28", ''),
    '1323': ('Turftorenstraat 21', ''),
    '1325': ('Uurwerkersgang 10', ''),
    '2111': ('Grote Rozenstraat 38', 'Nieuwenhuis building'),
    '2211': ('Grote Kruisstraat 2/1', 'Heymans building'),
    '2213': ('Grote Kruisstraat 2/1', 'Heymans building'),
    '2212': ('Grote Kruisstraat 2/1', 'Munting building'),
    '2221': ('Grote Rozenstraat 1', 'Bouman building'),
    '2222': ('Grote Rozenstraat 17', 'Gadourek building'),
    '2223': ('Grote Rozenstraat 15', 'Snijders building'),
    '2224': ('Grote Rozenstraat 3', 'Van Gelder building'),
    '2231': ("Nieuwe Kijk in 't Jatstraat 68/70", 'Jantina Tammes house'),
    '3111': ('Antonius Deusinglaan 2', ''),
    '3211': ('Antonius Deusinglaan 1', 'MWF complex (UMCG)'),
    '3227': ('Antonius Deusinglaan 1', 'Anda Kerkhoven Centre (HAC)'),
    '4122': ('Bloemstraat 36/36a', ''),
    '4123': ('Bloemstraat 36/36a', ''),
    '4335': ('A-weg 30', ''),
    '4336': ('Munnikeholm 10', 'USVA cultural student centre'),
    '4345': ('Hoendiepskade 23/24', ''),
    '4411': ('Visserstraat 47/49', ''),
    '4428': ('Grote Markt 21', 'Het Groot Handelshuis'),
    '4451': ('Oude Ebbingestraat 25', ''),
    '5111': ('Nijenborgh 4', 'Nijenborgh'),
    '5112': ('Nijenborgh 4', 'Nijenborgh'),
    '5113': ('Nijenborgh 4', 'Nijenborgh'),
    '5114': ('Nijenborgh 4', 'Nijenborgh'),
    '5115': ('Nijenborgh 4', 'Nijenborgh'),
    '5116': ('Nijenborgh 4', 'Nijenborgh'),
    '5143': ('Zernikelaan 1', 'Porters lodge'),
    '5161': ('Nijenborgh 9, 9747 AG Groningen, Nederland', 'Bernoulliborg'),
    '5158': ('Nijenborgh 6', 'Energy Academy Europa'),
    '5159': ('Nijenborgh 6', 'Energy Academy Europa'),
    '5171': ('Nijenborgh 7', 'Linnaeusborg'),
    '5172': ('Nijenborgh 7', 'Linnaeusborg'),
    '5173': ('Nijenborgh 7', 'Linnaeusborg'),
    '5174': ('Nijenborgh 7', 'Linnaeusborg'),
    '5211': ('Blauwborgje 16', 'Sports Centre'),
    '5231': ('Nadorstplein 2a', ''),
    '5236': ('Blauwborgje 8', ''),
    '5256': ('Blauwborgje 8-10', ''),
    '5263': ('Blauwborgje 4', 'Aletta Jacobs hal (examination hall)'),
    '5411': ('Nettelbosje 2', 'Duisenberg building'),
    '5412': ('Nettelbosje 2', ''),
    '5414': ('Nettelbosje 2', ''),
    '5415': ('Landleven 1', ''),
    '5416': ('Landleven 1', ''),
    '5417': ('Landleven 1', ''),
    '5419': ('Landleven 12', 'Kapteynborg'),
    '5431': ('Nettelbosje 1', 'Smitsborg'),
    '5433': ('Nettelbosje 2', ''),
    '5527': ('Kadijk 4', ''),
    '5612': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa building'),
    '5613': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa building'),
    '5614': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa building'),
    '5615': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa building'),
    '5616': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa building'),
    '5711': ('Zernikelaan 25', ''),
    '7112': ('Heereweg 10 Schiermonnikoog', 'De Herdershut'),
    '7117': ('Allersmaweg 64 Ezinge', 'Allersmaborg'),
    '7441': ('Wirdumerdijk 34 Leeuwarden', ''),
}


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

    if not rooms:
        return ""

    if len(rooms) > 1:
        return ", ".join(
            f"{room['code']} {room['displayNameEn']}"
            for room in rooms
        )

    room = rooms[0]
    building, _, room_number = room["code"].partition(".")

    if building not in BUILDINGS:
        return f"{room['code']} {room['displayNameEn']}"

    address, building_name = BUILDINGS[building]

    if building_name:
        name = f"{building_name} {room_number} {room['displayNameEn']}"
    else:
        name = f"{room['code']} {room['displayNameEn']}"

    return f"{name}\n{address}"


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
            traceback.print_exc()
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
