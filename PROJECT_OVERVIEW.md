# Lead Commander – Project Overview

## 1. Project Structure

<details>
<summary>lead_commander/ (root)</summary>

```
.
├── .gitignore
├── .gitnore
├── index.html
├── README_deploy.md
├── render.yaml
├── requirements.txt
├── style.css
├── frontend/
│   ├── app.py
│   └── requirements.txt
└── lead_commander_backend/
    ├── backend_server.py
    ├── README.md
    ├── requirements.txt
    └── app/
        ├── __init__.py
        ├── config.py
        ├── database.py
        ├── main.py
        ├── utils.py
        ├── agents/
        │   ├── automation_agent.py
        │   ├── coaching_agent.py
        │   ├── insight_agent.py
        │   ├── lead_intelligence_agent.py
        │   ├── market_signal_scanner.py
        │   ├── pipeline_optimization_agent.py
        │   └── revenue_forecasting_agent.py
        ├── models/
        │   ├── __init__.py
        │   └── lead.py
        ├── routes/
        │   ├── __init__.py
        │   ├── auth_routes.py
        │   ├── insight_routes.py
        │   └── lead_routes.py
        └── services/
            ├── __init__.py
            ├── db_service.py
            └── openai_service.py
```
</details>

## 2. Core Technologies and Frameworks

- **Frontend:** Streamlit (Python-based UI framework)
  - All UI appears to be handled via Streamlit (`frontend/app.py`)
  - No evidence of embedded HTML/CSS for the main UI (index.html and style.css may be for deployment or documentation)
- **Backend:** Custom Python backend (Flask-like structure, but not explicitly Flask)
  - Modular backend with agents, services, and API routes
- **Key Libraries (from requirements.txt):**
  - Streamlit
  - OpenAI SDK
  - Database libraries (likely SQLAlchemy or similar, see `database.py`)
  - Other AI/automation libraries as needed

## 3. Main Application Flow

- **Login Process:**  
  User authentication is likely handled via `lead_commander_backend/app/routes/auth_routes.py`.
- **Navigation:**  
  Streamlit sidebar provides navigation between pages (e.g., Upload Leads, View Leads, Optimize Pipeline).
- **Uploading Leads:**  
  Users upload lead files (CSV or similar) via a Streamlit file uploader.
- **Generating Insights:**  
  Uploaded leads are processed, and insights are generated using backend agents (e.g., insight_agent.py).
- **Viewing and Optimizing Leads:**  
  Users can view leads in a table, see AI-generated insights, and use optimization tools (pipeline_optimization_agent.py).

## 4. Major Python Scripts or Modules

- **frontend/app.py:**  
  Main Streamlit app; handles UI, navigation, and user interactions.
- **lead_commander_backend/backend_server.py:**  
  Entry point for backend server; likely runs API endpoints for frontend to consume.
- **lead_commander_backend/app/database.py:**  
  Database connection and ORM logic.
- **lead_commander_backend/app/agents/\***:  
  Specialized AI/automation agents for insights, coaching, pipeline optimization, etc.
- **lead_commander_backend/app/routes/\***:  
  API route handlers for authentication, insights, and lead management.
- **lead_commander_backend/app/services/db_service.py:**  
  Database service layer for CRUD operations.
- **lead_commander_backend/app/services/openai_service.py:**  
  Handles communication with OpenAI API for AI-powered features.

## 5. Known To-Do Items

No major to-do items or next steps were found in the project’s codebase or documentation. The code and documentation do not currently contain any outstanding "TODO" comments or "next steps" instructions.


