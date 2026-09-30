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
    '1111': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic Building'),
    '1112': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic Building'),
    '1113': ("Oude Kijk in Het Jatstraat 39, 9712 EB Groningen, Nederland", None),
    '1114': ("Oude Kijk in 't Jatstraat 41/41a, 9712 EB Groningen, Nederland", None),
    '1116': ('Broerstraat 5, 9712 CP Groningen, Nederland', 'Academic Building'),
    '1117': ('Muurstraat 14, 9712 EN Groningen, Nederland', None),
    '1121': ('Oude Boteringestraat 44, 9712 GL Groningen, Nederland', 'Administration Building'),
    '1124': ('Oude Boteringestraat 38, 9712 GK Groningen, Nederland', None),
    '1126': ('Oude Boteringestraat 34, 9712 GK Groningen, Nederland', None),
    '1131': ('Oude Boteringestraat 52, 9712 GL Groningen, Nederland', None),
    '1134': ('Broerstraat 9, 9712 CP Groningen, Nederland', None),
    '1211': ('Broerstraat 4, 9712 CP Groningen, Nederland', None),
    '1212': ('Poststraat 6, 9712 CP Groningen, Nederland', None),
    '1213': ("Oude Kijk in 't Jatstraat 7a, 9712 CP Groningen, Nederland", None),
    '1219': ("Oude Kijk in 't Jatstraat 7a, 9712 CP Groningen, Nederland", None),
    '1215': ("Oude Kijk in 't Jatstraat 9, 9712 EA Groningen, Nederland", None),
    '1217': ('Oude Boteringestraat 18, 9712 ER Groningen, Nederland', 'Röling Building'),
    '1221': ('Oude Boteringestraat 24, 9712 GH Groningen, Nederland', 'Calmershuis'),
    '1311': ("Oude Kijk in 't Jatstraat 26, 9712 GR Groningen, Nederland", 'Harmoniecomplex'),
    '1312': ("Oude Kijk in 't Jatstraat 26, 9712 GR Groningen, Nederland", 'Harmoniecomplex'),
    '1313': ("Oude Kijk in 't Jatstraat 26, 9712 GR Groningen, Nederland", 'Harmoniecomplex'),
    '1314': ("Oude Kijk in 't Jatstraat 26, 9712 GR Groningen, Nederland", 'Harmoniecomplex'),
    '1315': ("Oude Kijk in 't Jatstraat 26, 9712 GR Groningen, Nederland", 'Harmoniecomplex'),
    '1321': ("Oude Kijk in 't Jatstraat 28, 9712 EK Groningen, Nederland", None),
    '1323': ('Turftorenstraat 21, 9712 EK Groningen, Nederland', None),
    '1325': ('Uurwerkersgang 10, 9712 EJ Groningen, Nederland', None),
    '2111': ('Grote Rozenstraat 38, 9712 EK Groningen, Nederland', 'Nieuwenhuis Building'),
    '2211': ('Grote Kruisstraat 2/1, 9712 TH Groningen, Nederland', 'Heymans Building'),
    '2213': ('Grote Kruisstraat 2/1, 9712 TH Groningen, Nederland', 'Heymans Building'),
    '2212': ('Grote Kruisstraat 2/1, 9712 TH Groningen, Nederland', 'Munting Building'),
    '2221': ('Grote Rozenstraat 1, 9712 TG Groningen, Nederland', 'Bouman Building'),
    '2222': ('Grote Rozenstraat 17, 9712 TG Groningen, Nederland', 'Gadourek Building'),
    '2223': ('Grote Rozenstraat 15, 9712 TG Groningen, Nederland', 'Snijders Building'),
    '2224': ('Grote Rozenstraat 3, 9712 TG Groningen, Nederland', 'Van Gelder Building'),
    '2231': ("Nieuwe Kijk in 't Jatstraat 68/70, 9712 SK Groningen, Nederland", 'Jantina Tammes House'),
    '3111': ('Antonius Deusinglaan 2, 9713 AW Groningen, Nederland', None),
    '3211': ('Antonius Deusinglaan 1, 9713 AP Groningen, Nederland', 'MWF complex (UMCG)'),
    '3227': ('Antonius Deusinglaan 1, 9713 AP Groningen, Nederland', 'Anda Kerkhoven Centre (HAC)'),
    '4122': ('Bloemstraat 36/36a, 9712 LE Groningen, Nederland', None),
    '4123': ('Bloemstraat 36/36a, 9712 LE Groningen, Nederland', None),
    '4335': ('A-weg 30, 9718 CW Groningen, Nederland', None),
    '4336': ('Munnikeholm 10, 9711 JA Groningen, Nederland', 'USVA Cultural Student Centre'),
    '4345': ('Hoendiepskade 23/24, 9718 BG Groningen, Nederland', None),
    '4411': ('Visserstraat 47/49, 9712 CT Groningen, Nederland', None),
    '4428': ('Grote Markt 21, 9712 EK Groningen, Nederland', 'Het Groot Handelshuis'),
    '4451': ('Oude Ebbingestraat 25, 9712 HA Groningen, Nederland', None),
    '5111': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5112': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5113': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5114': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5115': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5116': ('Nijenborgh 4, 9747 AG Groningen, Nederland', 'Nijenborgh'),
    '5143': ('Zernikelaan 1, 9747 AA Groningen, Nederland', 'Porters Lodge'),
    '5161': ('Nijenborgh 9, 9747 AG Groningen, Nederland', 'Bernoulliborg'),
    '5158': ('Nijenborgh 6, 9747 AG Groningen, Nederland', 'Energy Academy Europa'),
    '5159': ('Nijenborgh 6, 9747 AG Groningen, Nederland', 'Energy Academy Europa'),
    '5171': ('Nijenborgh 7, 9747 AG Groningen, Nederland', 'Linnaeusborg'),
    '5172': ('Nijenborgh 7, 9747 AG Groningen, Nederland', 'Linnaeusborg'),
    '5173': ('Nijenborgh 7, 9747 AG Groningen, Nederland', 'Linnaeusborg'),
    '5174': ('Nijenborgh 7, 9747 AG Groningen, Nederland', 'Linnaeusborg'),
    '5211': ('Blauwborgje 16, 9747 AC Groningen, Nederland', 'Sports Centre'),
    '5231': ('Nadorstplein 2a, 9747 AC Groningen, Nederland', None),
    '5236': ('Blauwborgje 8, 9747 AC Groningen, Nederland', None),
    '5256': ('Blauwborgje 8-10, 9747 AC Groningen, Nederland', None),
    '5263': ('Blauwborgje 4, 9747 AC Groningen, Nederland', 'Aletta Jacobs Hal'),
    '5411': ('Nettelbosje 2, 9747 AE Groningen, Nederland', 'Duisenberg Building'),
    '5412': ('Nettelbosje 2, 9747 AE Groningen, Nederland', None),
    '5414': ('Nettelbosje 2, 9747 AE Groningen, Nederland', None),
    '5415': ('Landleven 1, 9747 AD Groningen, Nederland', None),
    '5416': ('Landleven 1, 9747 AD Groningen, Nederland', None),
    '5417': ('Landleven 1, 9747 AD Groningen, Nederland', None),
    '5419': ('Landleven 12, 9747 AD Groningen, Nederland', 'Kapteynborg'),
    '5431': ('Nettelbosje 1, 9747 AJ Groningen, Nederland', 'Smitsborg'),
    '5433': ('Nettelbosje 2, 9747 AE Groningen, Nederland', None),
    '5527': ('Kadijk 4, 9747 AT Groningen, Nederland', None),
    '5612': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa Building'),
    '5613': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa Building'),
    '5614': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa Building'),
    '5615': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa Building'),
    '5616': ('Nijenborgh 3, 9747 AG Groningen, Nederland', 'Feringa Building'),
    '5711': ('Zernikelaan 25, 9747 AA Groningen, Nederland', None),
    '7112': ('Heereweg 10, 9166 SE Schiermonnikoog, Nederland', 'De Herdershut'),
    '7117': ('Allersmaweg 64, 9891 TD Ezinge, Nederland', 'Allersmaborg'),
    '7441': ('Wirdumerdijk 34, 8911 CE Leeuwarden, Nederland', None),
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
    building = room["code"].split(".")[0]

    if building not in BUILDINGS:
        return f"{room['code']} {room['displayNameEn']}"

    address, building_name = BUILDINGS[building]

    if building_name:
        name = f"{room['code']} {building_name}"
    else:
        name = room['code']

    if room['displayNameEn']:
        name += f" - {room['displayNameEn']}"

    return f"{name}\n{address}"


def fetch_calendar(courses, objects):
    response = requests.post(
        ROOSTER_URL,
        json={
            "courseOfferingCodes": courses,
            "objects": objects,
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

    return calendar.serialize()


class CalendarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path not in ("/", "/rooster.ics", "/calendar.ics"):
            self.send_error(404)
            return

        query = parse_qs(url.query)

        # https://rooster.rug.nl/current?programmeOffering=199346&studentGroup=244807&room=115915&courseOffering=WBMA029-05.2026-2027.1

        course_offering_codes = []
        objects = []

        for q in query.get("courseOffering", ""):
            course_offering_codes += q.split(",")

        for q in query.get("programmeOffering", ""):
            objects += q.split(",")

        for q in query.get("studentGroup", ""):
            objects += q.split(",")

        for q in query.get("room", ""):
            objects += q.split(",")

        if not course_offering_codes and not objects:
            self.send_error(400)
            return

        try:
            calendar = fetch_calendar(course_offering_codes, objects)
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
    print("Serving calendar on http://0.0.0.0:6565/calendar.ics")
    server.serve_forever()
