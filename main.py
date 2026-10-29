from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json
import re
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "civicpulse.db"
FRONTEND = ROOT / "frontend"

app = FastAPI(
    title="CivicPulse API",
    description="Community issue reporting, explainable prioritization, and response tracking.",
    version="1.0.0",
)

CATEGORY_RISK = {
    "Water & Sanitation": 22,
    "Roads & Potholes": 18,
    "Waste Management": 16,
    "Street Lighting": 14,
    "Public Safety": 28,
    "Parks & Public Spaces": 10,
    "Other": 8,
}
STATUS_VALUES = {"Reported", "In Progress", "Resolved"}
SEVERITY_POINTS = {"Low": 5, "Medium": 12, "High": 20, "Critical": 28}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def priority_for(category, severity, affected_people, created_at):
    base = CATEGORY_RISK.get(category, 8)
    sev = SEVERITY_POINTS.get(severity, 5)
    people = min(20, max(0, int(affected_people or 0)) // 10)
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_hours = max(0, (datetime.now(timezone.utc) - created).total_seconds() / 3600)
    except Exception:
        age_hours = 0
    freshness = min(10, int(age_hours // 24))
    score = min(100, base + sev + people + freshness)
    reasons = [
        f"{category} risk contribution: {base}/28",
        f"{severity} severity contribution: {sev}/28",
        f"Estimated affected people contribution: {people}/20",
        f"Report-age contribution: {freshness}/10",
    ]
    label = "Critical" if score >= 75 else "High" if score >= 58 else "Medium" if score >= 38 else "Low"
    return score, label, reasons


def normalize(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def is_similar(a, b):
    if a["category"] != b["category"]:
        return False
    loc_a = normalize(a["location"])
    loc_b = normalize(b["location"])
    desc_a = normalize(a["description"])
    desc_b = normalize(b["description"])
    loc_overlap = len(loc_a & loc_b) / max(1, len(loc_a | loc_b))
    desc_overlap = len(desc_a & desc_b) / max(1, len(desc_a | desc_b))
    return loc_overlap >= 0.45 and desc_overlap >= 0.22


def row_to_issue(row, all_rows=None):
    item = dict(row)
    score, label, reasons = priority_for(
        item["category"], item["severity"], item["affected_people"], item["created_at"]
    )
    item["priority_score"] = score
    item["priority_label"] = label
    item["priority_reasons"] = reasons
    item["possible_duplicates"] = []
    if all_rows is not None:
        for other in all_rows:
            if other["id"] != item["id"] and is_similar(item, dict(other)):
                item["possible_duplicates"].append(other["id"])
    return item


def seed_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                affected_people INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'Reported',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
        if count == 0:
            samples = [
                ("Water leaking near public tap", "Water & Sanitation", "Gandhi Nagar bus stop", "Continuous water leak near the public drinking tap; road is getting slippery.", "High", 75, "Reported", now_iso()),
                ("Large pothole near school gate", "Roads & Potholes", "Government school main gate", "Deep pothole near the school gate creates risk for students and two-wheelers.", "Critical", 120, "In Progress", now_iso()),
                ("Garbage not collected", "Waste Management", "Market Street east lane", "Mixed waste has remained near the market for several days and attracts stray animals.", "High", 90, "Reported", now_iso()),
                ("Streetlight not working", "Street Lighting", "Lake Road, 2nd cross", "Streetlight is not working on a dark stretch used by pedestrians at night.", "Medium", 35, "Resolved", now_iso()),
                ("Broken park swing", "Parks & Public Spaces", "Community park play area", "A damaged swing needs inspection before children use the play area.", "Medium", 20, "Reported", now_iso()),
            ]
            conn.executemany("""
                INSERT INTO issues (title, category, location, description, severity, affected_people, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, samples)


seed_db()


class IssueCreate(BaseModel):
    title: str = Field(min_length=4, max_length=100)
    category: str
    location: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    severity: str
    affected_people: int = Field(default=1, ge=1, le=100000)


class StatusUpdate(BaseModel):
    status: str


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CivicPulse API"}


@app.get("/api/issues")
def list_issues(
    search: Optional[str] = Query(default=None, max_length=120),
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM issues ORDER BY created_at DESC, id DESC").fetchall()
    all_rows = [dict(r) for r in rows]
    result = []
    for row in rows:
        item = row_to_issue(row, all_rows)
        if search and search.lower() not in " ".join([
            item["title"], item["location"], item["description"], item["category"]
        ]).lower():
            continue
        if category and category != "All Categories" and item["category"] != category:
            continue
        if status and status != "All Statuses" and item["status"] != status:
            continue
        if priority and priority != "All Priorities" and item["priority_label"] != priority:
            continue
        result.append(item)
    return result


@app.post("/api/issues", status_code=201)
def create_issue(payload: IssueCreate):
    if payload.category not in CATEGORY_RISK:
        raise HTTPException(status_code=400, detail="Unsupported category.")
    if payload.severity not in SEVERITY_POINTS:
        raise HTTPException(status_code=400, detail="Unsupported severity.")
    stamp = now_iso()
    with connect() as conn:
        cur = conn.execute("""
            INSERT INTO issues (title, category, location, description, severity, affected_people, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Reported', ?, ?)
        """, (
            payload.title.strip(), payload.category, payload.location.strip(),
            payload.description.strip(), payload.severity, payload.affected_people, stamp, stamp
        ))
        issue_id = cur.lastrowid
        row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        all_rows = conn.execute("SELECT * FROM issues").fetchall()
    return row_to_issue(row, [dict(r) for r in all_rows])


@app.patch("/api/issues/{issue_id}")
def update_status(issue_id: int, payload: StatusUpdate):
    if payload.status not in STATUS_VALUES:
        raise HTTPException(status_code=400, detail="Status must be Reported, In Progress, or Resolved.")
    with connect() as conn:
        exists = conn.execute("SELECT id FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Issue not found.")
        conn.execute("UPDATE issues SET status = ?, updated_at = ? WHERE id = ?",
                     (payload.status, now_iso(), issue_id))
        row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        all_rows = conn.execute("SELECT * FROM issues").fetchall()
    return row_to_issue(row, [dict(r) for r in all_rows])


@app.get("/api/analytics")
def analytics():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM issues").fetchall()
    issues = [row_to_issue(r) for r in rows]
    by_category = {}
    for issue in issues:
        by_category[issue["category"]] = by_category.get(issue["category"], 0) + 1
    return {
        "total": len(issues),
        "open": sum(1 for x in issues if x["status"] != "Resolved"),
        "in_progress": sum(1 for x in issues if x["status"] == "In Progress"),
        "resolved": sum(1 for x in issues if x["status"] == "Resolved"),
        "high_priority": sum(1 for x in issues if x["priority_label"] in ("High", "Critical") and x["status"] != "Resolved"),
        "resolution_rate": round(100 * sum(1 for x in issues if x["status"] == "Resolved") / max(1, len(issues))),
        "by_category": by_category,
    }


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
