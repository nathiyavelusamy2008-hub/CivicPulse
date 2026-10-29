# CivicPulse — Community Impact Intelligence Platform

**Turn community reports into prioritized, trackable action.**

CivicPulse is a full-stack civic issue reporting and response platform. Residents can report local problems such as water leaks, garbage overflow, potholes, broken streetlights, and unsafe public spaces. The backend calculates a transparent priority score, flags possible duplicate reports, and gives responders a dashboard to track progress.

## Why it is different
- **Transparent urgency scoring:** combines severity, public-safety risk, affected people, and report freshness.
- **Duplicate awareness:** identifies reports with similar categories and nearby locations to reduce repeated work.
- **Closed-loop accountability:** every report has a status and timeline-friendly tracking.
- **Impact dashboard:** shows open issues, high-priority cases, resolved reports, and category distribution.
- **Demo-ready:** comes with sample cases and a local SQLite database; no API key is required.

## Features
- Submit a civic issue with category, location, description, and estimated number of people affected.
- Browse, search, and filter reports.
- See priority score and the reason behind it.
- Update report status from the responder controls.
- View live dashboard metrics.
- Persist reports in SQLite.

## Tech stack
- Frontend: HTML, CSS, vanilla JavaScript
- Backend: Python, FastAPI
- Database: SQLite
- API documentation: FastAPI Swagger UI

## Run locally

### 1. Requirements
- Python 3.10 or newer

### 2. Install dependencies
Open a terminal in the project folder:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Then:
```bash
pip install -r requirements.txt
```

### 3. Start the application
```bash
uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

API docs: **http://127.0.0.1:8000/docs**

## Project structure
```text
CivicPulse-Community-Impact-Platform/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
├── .env.example
└── README.md
```

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/issues` | List reports, with optional filters |
| POST | `/api/issues` | Create a report |
| PATCH | `/api/issues/{id}` | Update status |
| GET | `/api/analytics` | Dashboard metrics |
| GET | `/api/health` | Service health |

## Priority score
The score is a **demo heuristic, not an official emergency assessment**. It considers category risk, user-selected severity, estimated affected people, and report age. The interface displays the main reason so the score is explainable.

## Demo walkthrough
1. Open the dashboard and review the sample reports.
2. Submit a report for a water leak or pothole.
3. Review the calculated score and possible duplicate warning.
4. Filter to high-priority issues.
5. Change a report from **Reported** to **In Progress** or **Resolved**.
6. Watch the dashboard metrics update.

## Important limitations
- The included reports are illustrative demo data, not live government data.
- Location is entered as text; map geocoding and GPS are not integrated.
- The priority score supports triage but must not replace human review, official emergency channels, or professional judgement.
- Do not submit personal, confidential, or emergency-sensitive information.

## Future enhancements
- Map-based issue visualization and GPS capture
- Image upload with privacy safeguards
- Verified department accounts and role-based access
- SMS/email notifications
- Multilingual reporting
- Optional AI model for report classification, with human review

## Vision
**A community where no local issue disappears into silence.**
