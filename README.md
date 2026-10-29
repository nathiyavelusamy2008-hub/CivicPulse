# ✳ CivicPulse — Community Impact Intelligence Platform

### Turning Community Problems into Prioritized Action

CivicPulse is a full-stack civic technology platform designed to help communities report local issues, identify urgent problems, and track their resolution. From potholes and water leakage to waste management and broken streetlights, CivicPulse transforms community reports into actionable insights using transparent priority scoring and duplicate-report detection.

Our mission is to build more responsive, transparent, and accountable communities through technology.

## 🚨 Problem Statement

Communities frequently face local infrastructure and public-service issues, including:

- Delayed identification and resolution of civic problems.
- Difficulty prioritizing issues based on urgency and public impact.
- Repeated reports of the same issue.
- Limited visibility into the progress of reported problems.
- Lack of centralized information for tracking community improvement.

These challenges can lead to wasted resources, delayed responses, and reduced public trust.

## 💡 Our Solution

CivicPulse provides a centralized platform where users can report civic issues and responders can prioritize and manage them efficiently.

The system calculates an explainable priority score using factors such as issue category, severity, estimated affected population, and report age. It also flags potentially similar reports and provides a dashboard to monitor issue status and resolution progress.

## ✨ Key Features

### 📊 1. Community Impact Dashboard
- View total submitted reports.
- Monitor unresolved issues.
- Track high-priority reports.
- View the overall resolution rate.

### 📝 2. Civic Issue Reporting
- Submit issues with a title, category, location, and description.
- Select severity levels from Low to Critical.
- Enter an estimate of the number of people affected.
- Store reports in a persistent database.

### 🧠 3. Explainable Priority Scoring
- Calculate a priority score out of 100.
- Consider category risk, severity, affected people, and report age.
- Display the reasons contributing to each score.
- Help responders organize their work more effectively.

### 🔍 4. Duplicate-Report Detection
- Identify potentially similar reports.
- Compare issue categories, locations, and descriptions.
- Help reduce duplicate work and improve coordination.

### 🔄 5. Issue Status Tracking
Track every report through three statuses:

- **Reported** — The issue has been submitted.
- **In Progress** — Work on the issue has started.
- **Resolved** — The issue has been marked as resolved.

### 🔎 6. Search and Filtering
- Search by issue title, location, description, or category.
- Filter reports by category, priority, and status.
- Find relevant reports quickly.

### 🗄️ 7. Database Integration
- Store civic reports using SQLite.
- Retrieve reports through backend API endpoints.
- Preserve submitted data across application restarts.

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| API Testing | FastAPI Swagger UI |
| Development Server | Uvicorn |

## 🏗️ System Architecture

```text
       Community Members
               |
               v
      Frontend Web Interface
         HTML / CSS / JS
               |
               v
          FastAPI Backend
               |
       +-------+--------+
       |                |
       v                v
 Priority Scoring   Duplicate Detection
       |                |
       +-------+--------+
               |
               v
         SQLite Database
               |
               v
       Impact Dashboard
    Reports, Priorities, Status
```

## 🔄 Application Workflow

1. A community member submits a civic issue.
2. The backend validates the submitted information.
3. The issue is stored in the SQLite database.
4. A priority score is calculated using the configured scoring rules.
5. Similar reports are checked and potential duplicates are flagged.
6. The dashboard displays the report and its priority.
7. Responders update the issue status as work progresses.
8. Dashboard statistics refresh to reflect the latest information.

## 🛠️ Installation and Setup

### Prerequisites

- Python 3.10 or newer
- Visual Studio Code or another code editor
- A modern web browser

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CivicPulse-Community-Impact-Platform
```

Replace the placeholder with your actual GitHub repository URL.

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

### Step 3: Activate the environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Start the application

Run this command from the project root directory:

```bash
uvicorn backend.main:app --reload
```

### Step 6: Open the application

- **Web application:** http://127.0.0.1:8000
- **API documentation:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/api/health

The application initializes its SQLite database and adds sample reports when the database is empty.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend availability |
| GET | `/api/issues` | Retrieve and filter reports |
| POST | `/api/issues` | Submit a new report |
| PATCH | `/api/issues/{id}` | Update report status |
| GET | `/api/analytics` | Retrieve dashboard statistics |

## 🌍 Real-World Applications

CivicPulse can serve as a prototype for:

- Municipal complaint management.
- Community infrastructure monitoring.
- Public-space maintenance.
- Waste management coordination.
- Local road and streetlight issue tracking.
- Community-driven urban improvement initiatives.

## 🚀 Future Enhancements

- Interactive maps with GPS-based issue locations.
- Image uploads for visual evidence.
- AI-assisted classification of issue descriptions and images.
- Multilingual reporting for regional communities.
- Role-based access for administrators and response teams.
- Notifications when issue statuses change.
- Integration with verified municipal data and service workflows.
- Analytics to identify recurring problem areas.

## 🔐 Limitations and Responsible Use

- The included sample reports are illustrative, not live municipal records.
- Priority scores use a configurable rule-based heuristic and are not validated emergency-risk assessments.
- Duplicate detection identifies possible matches and does not guarantee that two reports describe the same incident.
- The current prototype does not include authenticated user accounts or verified department workflows.
- Critical emergencies should always be reported through official emergency channels.

## 🎯 Project Objectives

- Improve visibility into local civic problems.
- Support transparent and explainable issue prioritization.
- Reduce duplicate reporting and unnecessary effort.
- Make issue status and progress easier to track.
- Encourage community participation and accountability.

## 🌟 Our Vision

We envision communities where local problems are visible, priorities are understandable, and progress can be tracked.

**CivicPulse — Every Report Matters. Every Action Counts.**

---

*Developed as a civic technology prototype demonstrating full-stack web development, data management, explainable prioritization, and community-focused problem-solving.*

