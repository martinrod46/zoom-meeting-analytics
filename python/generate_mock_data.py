"""
generate_mock_data.py
=====================
Zoom Meeting Analytics Platform — Phase 1: Data Generation
-----------------------------------------------------------
Generates four realistic CSV files that simulate a Zoom data warehouse:
  - zoom_departments.csv   (12 rows)
  - zoom_hosts.csv         (150 rows)
  - zoom_meetings.csv      (2,000 rows)
  - zoom_participants.csv  (~18,000 rows, ~9 per meeting on average)

Usage:
    python generate_mock_data.py

Output:
    All CSVs are written to the same directory as this script.
    A seed is fixed so output is fully reproducible.

Author: Portfolio Project — Zoom Meeting Analytics Platform
"""

import random
import math
import csv
import os
import pandas as pd
from datetime import datetime, timedelta, date

# ── Configuration ─────────────────────────────────────────────────────────────
RANDOM_SEED        = 42          # Fixed seed → reproducible data
NUM_MEETINGS       = 2_000
NUM_HOSTS          = 150
OUTPUT_DIR         = os.path.dirname(os.path.abspath(__file__))
DATE_RANGE_START   = date(2023, 1, 1)
DATE_RANGE_END     = date(2024, 12, 31)

random.seed(RANDOM_SEED)

# ── Reference Data ────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
    "William","Barbara","David","Elizabeth","Richard","Susan","Joseph","Jessica",
    "Thomas","Sarah","Charles","Karen","Christopher","Lisa","Daniel","Nancy",
    "Matthew","Betty","Anthony","Margaret","Mark","Sandra","Donald","Ashley",
    "Steven","Dorothy","Paul","Kimberly","Andrew","Emily","Joshua","Donna",
    "Kenneth","Michelle","Kevin","Carol","Brian","Amanda","George","Melissa",
    "Timothy","Deborah","Ronald","Stephanie","Edward","Rebecca","Jason","Sharon",
    "Jeffrey","Laura","Ryan","Cynthia","Jacob","Kathleen","Gary","Amy",
    "Nicholas","Angela","Eric","Shirley","Jonathan","Anna","Stephen","Brenda",
    "Larry","Pamela","Justin","Emma","Scott","Nicole","Brandon","Helen",
    "Benjamin","Samantha","Samuel","Katherine","Raymond","Christine","Gregory",
    "Debra","Frank","Rachel","Alexander","Carolyn","Patrick","Janet","Jack",
    "Maria","Dennis","Heather","Jerry","Ann","Tyler","Diane","Aaron","Julie",
    "Jose","Joyce","Adam","Victoria","Nathan","Kelly","Henry","Christina",
    "Douglas","Lauren","Zachary","Joan","Peter","Evelyn","Kyle","Olivia",
    "Walter","Judith","Ethan","Megan","Jeremy","Cheryl","Harold","Martha",
    "Carl","Andrea","Keith","Frances","Roger","Hannah","Gerald","Jacqueline",
    "Christian","Gloria","Terry","Teresa","Sean","Kathryn","Austin","Sara",
    "Arthur","Janice","Noah","Jean","Lawrence","Alice","Jesse","Madison",
    "Bryan","Doris","Billy","Abigail","Joe","Julia","Jordan","Grace"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
    "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker",
    "Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell",
    "Carter","Roberts","Gomez","Phillips","Evans","Turner","Diaz","Parker",
    "Cruz","Edwards","Collins","Reyes","Stewart","Morris","Morales","Murphy",
    "Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper","Peterson","Bailey",
    "Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson","Watson",
    "Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster",
    "Jimenez","Powell","Jenkins","Perry","Russell","Sullivan","Bell","Coleman"
]

EMAIL_DOMAINS = [
    "zoomcorp.com", "zoomcorp.io", "zoomcorp-team.com",
    "corp.zoomanalytics.com", "internal.zoom.us"
]

MEETING_TYPES = ["Internal", "External", "Webinar", "Training"]
MEETING_TYPE_WEIGHTS = [0.55, 0.20, 0.10, 0.15]

DEVICE_TYPES = ["Desktop", "Mobile", "Web", "Room System"]
DEVICE_WEIGHTS = [0.58, 0.22, 0.14, 0.06]

SENIORITY_LEVELS = ["Junior", "Mid", "Senior", "Director"]
SENIORITY_WEIGHTS = [0.20, 0.40, 0.30, 0.10]

REGIONS = ["AMER", "EMEA", "APAC"]
REGION_WEIGHTS = [0.50, 0.30, 0.20]

# Business hours vary by region
REGION_HOUR_RANGES = {
    "AMER": (8, 18),
    "EMEA": (7, 17),
    "APAC": (9, 19),
}

WEEKDAYS = [0, 1, 2, 3, 4]  # Monday–Friday only (realistic)


# ── Utility Functions ─────────────────────────────────────────────────────────
def random_date(start: date, end: date) -> date:
    """Return a random weekday date between start and end."""
    delta_days = (end - start).days
    for _ in range(100):  # Max 100 tries to land on a weekday
        candidate = start + timedelta(days=random.randint(0, delta_days))
        if candidate.weekday() in WEEKDAYS:
            return candidate
    return start  # Fallback

def weighted_choice(options: list, weights: list):
    """Weighted random selection from a list."""
    return random.choices(options, weights=weights, k=1)[0]

def make_email(first: str, last: str, domain: str) -> str:
    """Generate a realistic corporate email address."""
    patterns = [
        f"{first.lower()}.{last.lower()}@{domain}",
        f"{first[0].lower()}{last.lower()}@{domain}",
        f"{first.lower()}{last[0].lower()}@{domain}",
    ]
    return random.choice(patterns)

def clamp(value, lo, hi):
    return max(lo, min(hi, value))

def fmt_ts(d: date, hour: int, minute: int) -> str:
    """Format a timestamp string from date + time components."""
    return datetime(d.year, d.month, d.day, hour, minute).strftime("%Y-%m-%d %H:%M:%S")


# ── Step 1: Generate Departments ─────────────────────────────────────────────
def generate_departments() -> pd.DataFrame:
    print("  Generating departments...")
    rows = [
        ("DEPT-001", "Engineering",       "Product & Technology",  "CC-101", 340),
        ("DEPT-002", "Product",           "Product & Technology",  "CC-102", 95),
        ("DEPT-003", "Design",            "Product & Technology",  "CC-103", 60),
        ("DEPT-004", "Data & Analytics",  "Product & Technology",  "CC-104", 75),
        ("DEPT-005", "Sales",             "Revenue",               "CC-201", 210),
        ("DEPT-006", "Marketing",         "Revenue",               "CC-202", 130),
        ("DEPT-007", "Customer Success",  "Revenue",               "CC-203", 185),
        ("DEPT-008", "Finance",           "Operations",            "CC-301", 80),
        ("DEPT-009", "Legal",             "Operations",            "CC-302", 35),
        ("DEPT-010", "HR & People",       "Operations",            "CC-303", 65),
        ("DEPT-011", "IT & Security",     "Operations",            "CC-304", 90),
        ("DEPT-012", "Executive",         "Leadership",            "CC-401", 20),
    ]
    df = pd.DataFrame(rows, columns=[
        "department_id", "department_name", "division", "cost_center", "headcount"
    ])
    print(f"    → {len(df)} departments created")
    return df


# ── Step 2: Generate Hosts ────────────────────────────────────────────────────
def generate_hosts(departments: pd.DataFrame) -> pd.DataFrame:
    print(f"  Generating {NUM_HOSTS} hosts...")
    dept_ids = departments["department_id"].tolist()
    # Weight distribution: more hosts in larger depts
    dept_weights = departments["headcount"].tolist()

    rows = []
    used_emails = set()

    hire_start = date(2018, 1, 1)
    hire_end   = date(2023, 6, 30)

    for i in range(1, NUM_HOSTS + 1):
        host_id    = f"HOST-{i:04d}"
        first      = random.choice(FIRST_NAMES)
        last       = random.choice(LAST_NAMES)
        dept_id    = weighted_choice(dept_ids, dept_weights)
        seniority  = weighted_choice(SENIORITY_LEVELS, SENIORITY_WEIGHTS)
        region     = weighted_choice(REGIONS, REGION_WEIGHTS)
        hire_date  = random_date(hire_start, hire_end)
        domain     = random.choice(EMAIL_DOMAINS)

        # Ensure unique email
        base_email = make_email(first, last, domain)
        email = base_email
        suffix = 1
        while email in used_emails:
            email = base_email.replace("@", f"{suffix}@")
            suffix += 1
        used_emails.add(email)

        rows.append({
            "host_id":        host_id,
            "full_name":      f"{first} {last}",
            "email":          email,
            "department_id":  dept_id,
            "seniority_level": seniority,
            "region":         region,
            "hire_date":      hire_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)
    print(f"    → {len(df)} hosts created")
    return df


# ── Step 3: Generate Meetings ─────────────────────────────────────────────────
def generate_meetings(hosts: pd.DataFrame, departments: pd.DataFrame) -> pd.DataFrame:
    print(f"  Generating {NUM_MEETINGS} meetings...")

    host_ids   = hosts["host_id"].tolist()
    dept_ids   = departments["department_id"].tolist()

    # Map host → region for realistic meeting hours
    host_region = dict(zip(hosts["host_id"], hosts["region"]))

    rows = []
    for i in range(1, NUM_MEETINGS + 1):
        meeting_id   = f"ZM-{random.randint(10000000, 99999999)}"
        host_id      = random.choice(host_ids)
        dept_id      = random.choice(dept_ids)
        meeting_type = weighted_choice(MEETING_TYPES, MEETING_TYPE_WEIGHTS)
        meeting_date = random_date(DATE_RANGE_START, DATE_RANGE_END)

        # Scheduled duration depends on meeting type
        if meeting_type == "Webinar":
            sched_duration = random.choice([60, 90, 120])
        elif meeting_type == "Training":
            sched_duration = random.choice([60, 90, 120, 180])
        elif meeting_type == "External":
            sched_duration = random.choice([30, 45, 60])
        else:
            sched_duration = random.choice([15, 30, 45, 60, 90])

        # Actual duration: most meetings run close to scheduled (+/- variance)
        variance_pct = random.gauss(mu=0.0, sigma=0.15)   # ±15% normal dist
        actual_duration = clamp(
            round(sched_duration * (1 + variance_pct)),
            5,
            sched_duration + 60
        )

        # Meeting start time — within business hours for host's region
        region = host_region.get(host_id, "AMER")
        hour_lo, hour_hi = REGION_HOUR_RANGES[region]
        start_hour   = random.randint(hour_lo, hour_hi - 1)
        start_minute = random.choice([0, 15, 30, 45])

        # Invitees and attendance
        if meeting_type == "Webinar":
            total_invited = random.randint(50, 500)
            attendance_rate = random.gauss(0.55, 0.12)
        elif meeting_type == "Training":
            total_invited = random.randint(10, 50)
            attendance_rate = random.gauss(0.85, 0.08)
        elif meeting_type == "External":
            total_invited = random.randint(2, 12)
            attendance_rate = random.gauss(0.80, 0.10)
        else:  # Internal
            total_invited = random.randint(3, 30)
            attendance_rate = random.gauss(0.75, 0.12)

        attendance_rate = clamp(attendance_rate, 0.20, 1.0)
        total_joined    = clamp(round(total_invited * attendance_rate), 1, total_invited)

        # Engagement signals — correlated: longer, larger meetings = less engagement
        engagement_decay = 1 - (math.log1p(total_joined) / 10)
        chat_messages    = max(0, round(random.gauss(
            mu = total_joined * 1.5 * engagement_decay,
            sigma = total_joined * 0.8
        )))
        reactions        = max(0, round(random.gauss(
            mu = total_joined * 0.8 * engagement_decay,
            sigma = total_joined * 0.5
        )))
        screen_shares    = max(0, round(random.gauss(
            mu = 2.5 * engagement_decay,
            sigma = 1.5
        )))
        recording        = random.random() < (0.70 if meeting_type in ("Webinar", "Training") else 0.35)

        rows.append({
            "meeting_id":             meeting_id,
            "host_id":                host_id,
            "department_id":          dept_id,
            "meeting_date":           meeting_date.strftime("%Y-%m-%d"),
            "start_time":             fmt_ts(meeting_date, start_hour, start_minute),
            "scheduled_duration_min": sched_duration,
            "actual_duration_min":    actual_duration,
            "meeting_type":           meeting_type,
            "total_invited":          total_invited,
            "total_joined":           total_joined,
            "recording_enabled":      recording,
            "chat_messages_count":    chat_messages,
            "reactions_count":        reactions,
            "screen_shares_count":    screen_shares,
        })

    df = pd.DataFrame(rows)
    print(f"    → {len(df)} meetings created")
    return df


# ── Step 4: Generate Participants ─────────────────────────────────────────────
def generate_participants(meetings: pd.DataFrame) -> pd.DataFrame:
    print("  Generating participants (this is the large table — please wait)...")

    rows = []
    participant_counter = 1

    for _, meeting in meetings.iterrows():
        n_participants = int(meeting["total_joined"])
        meeting_date_str = meeting["meeting_date"]
        start_ts_str     = meeting["start_time"]
        actual_dur       = int(meeting["actual_duration_min"])
        meeting_id       = meeting["meeting_id"]

        start_dt = datetime.strptime(start_ts_str, "%Y-%m-%d %H:%M:%S")
        end_dt   = start_dt + timedelta(minutes=actual_dur)

        for _ in range(n_participants):
            pid = f"PART-{participant_counter:07d}"
            participant_counter += 1

            # Join/leave time — most join within 3 min of start
            join_offset_min  = max(0, round(random.gauss(mu=1.5, sigma=2.0)))
            join_offset_min  = min(join_offset_min, actual_dur - 1)
            join_dt          = start_dt + timedelta(minutes=join_offset_min)

            # Some participants leave early
            early_leave_prob = 0.25
            if random.random() < early_leave_prob:
                leave_offset = random.randint(
                    join_offset_min + 5,
                    max(join_offset_min + 6, actual_dur - 5)
                )
            else:
                leave_offset = actual_dur + round(random.gauss(0, 1))

            leave_dt = start_dt + timedelta(minutes=clamp(leave_offset, join_offset_min + 1, actual_dur + 10))
            time_in_meeting = max(1, round((leave_dt - join_dt).total_seconds() / 60))

            # Camera / mic usage — correlated with attentiveness
            base_attentiveness = random.gauss(mu=0.72, sigma=0.18)
            camera_on_pct  = clamp(round(random.gauss(base_attentiveness * 0.8,  0.15), 2), 0.0, 1.0)
            mic_on_pct     = clamp(round(random.gauss(base_attentiveness * 0.55, 0.18), 2), 0.0, 1.0)
            attentiveness  = clamp(round(base_attentiveness * 100, 1), 0.0, 100.0)

            raised_hand    = random.random() < 0.08  # ~8% raise hand
            device_type    = weighted_choice(DEVICE_TYPES, DEVICE_WEIGHTS)

            first = random.choice(FIRST_NAMES)
            last  = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)
            email = make_email(first, last, domain)

            rows.append({
                "participant_id":       pid,
                "meeting_id":           meeting_id,
                "user_email":           email,
                "join_time":            join_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "leave_time":           leave_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "time_in_meeting_min":  time_in_meeting,
                "camera_on_pct":        camera_on_pct,
                "mic_on_pct":           mic_on_pct,
                "attentiveness_score":  attentiveness,
                "raised_hand":          raised_hand,
                "device_type":          device_type,
            })

    df = pd.DataFrame(rows)
    print(f"    → {len(df):,} participant records created")
    return df


# ── Step 5: Save CSVs ─────────────────────────────────────────────────────────
def save_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    size_kb = os.path.getsize(path) / 1024
    print(f"    ✓ Saved {filename}  ({len(df):,} rows, {size_kb:.1f} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Zoom Meeting Analytics — Mock Data Generator")
    print(f"  Seed: {RANDOM_SEED}  |  Meetings: {NUM_MEETINGS:,}  |  Hosts: {NUM_HOSTS}")
    print("=" * 60)

    departments  = generate_departments()
    hosts        = generate_hosts(departments)
    meetings     = generate_meetings(hosts, departments)
    participants = generate_participants(meetings)

    print("\nSaving CSV files...")
    save_csv(departments,  "zoom_departments.csv")
    save_csv(hosts,        "zoom_hosts.csv")
    save_csv(meetings,     "zoom_meetings.csv")
    save_csv(participants, "zoom_participants.csv")

    print("\n" + "=" * 60)
    print("  Data generation complete!")
    print(f"  Total records generated: {len(departments) + len(hosts) + len(meetings) + len(participants):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
