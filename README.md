# Document Intake Assistant

An intelligent, full-stack conversational document intake application powered by Google's official **Gemini API** (`google-genai` SDK) and Pydantic structured outputs. It conducts intake interviews, extracts and validates structured state separately from conversation history, detects ambiguities and contradictions without silent overwrites, rejects irrelevant answers, and generates a formal, fictional **Personal Wishes Document**.

---

## 🌟 Overview

Traditional estate and legal intake forms are overwhelming and error-prone. The **Document Intake Assistant** replaces static forms with an empathetic, highly structured conversational interview powered by Google Gemini.

Rather than relying on the LLM's raw context window or allowing an AI model alone to steer the intake flow, the application implements a strict **multi-stage validation pipeline**:
1. **Gemini understands natural language**: extracts structured JSON with strict Pydantic schemas.
2. **Pydantic validates the schema**: ensures types, structure, and constraints are met.
3. **Backend business rules validate meaning**: enforces legal/domain logic (e.g. child rules, gifts, boolean answers).
4. **MongoDB persists state**: source of truth for the session.
5. **Deterministic Question Controller**: decides next action and field, preventing loops and skipped fields.

---

## ✨ Key Features & Gemini API Capabilities

- **Google Gemini API with Structured Extraction**: Built using the modern official `google-genai` SDK with native JSON schema Pydantic models (`GeminiExtractionResult`).
- **Multi-Field Extraction**: Extracts all relevant information mentioned in a single user message (e.g. name, address, children status, and executor) and marks them as confirmed in one turn.
- **Strict Input Validation & Irrelevant Answer Rejection**: If the user goes off-topic (e.g., *"I like playing cricket"* when asked for address), the input is rejected, state is not polluted, and the assistant politely asks again.
- **Ambiguity Detection**: Non-committal answers (e.g., *"Maybe I'll have children in the future"*) are flagged as `AMBIGUOUS` without advancing state or setting arbitrary booleans.
- **Contradiction Guard**: Detects conflicts between prior and new statements (e.g., *"no children"* vs *"my children Sarah and Michael"*) without blindly overwriting state until confirmed.
- **Explicit Correction Recognition**: Automatically detects user correction phrases (*"actually"*, *"instead of"*, *"change to"*, *"make that"*) and updates specific fields directly.
- **Structured Gifts & Wishes Model**: Separates gifts into `{item, recipient_name, relationship, description}` and formats additional wishes cleanly.
- **Deterministic Question Controller**: Backend enforces question ordering, missing field calculation, and completion checks. Gemini never unilaterally decides interview completion.
- **Dual Fallback & High Reliability**: If Gemini API experiences rate limits or connectivity issues, automatic retries with backoff and deterministic fallback question maps guarantee the conversation never terminates.
- **Live Structured Information Panel**: Real-time side-panel displaying fields, completion percentage, and status indicators (`Confirmed`, `Pending`, `Not Applicable`).
- **Live Document Preview & Export**: Renders a formal fictional Personal Wishes Document with clean legal typography, draft disclaimer, and signature blocks.
- **Interactive Review & Edit Page**: Dedicated `/review` page enabling direct inline editing of any field via modal with immediate MongoDB and document sync.

---

## 🏗️ Architecture

```
                  USER
                   │
                   ▼
             REACT FRONTEND
                   │
                   ▼
              FASTAPI API
                   │
                   ▼
        LOAD CURRENT SESSION
                   │
                   ▼
          LOAD STRUCTURED STATE
                   │
                   ▼
            GEMINI EXTRACTOR (google-genai SDK)
                   │
                   ▼
          STRUCTURED JSON (Pydantic Schema)
                   │
                   ▼
        PYDANTIC VALIDATION
                   │
                   ▼
      BUSINESS RULE VALIDATION
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
        VALID   AMBIGUOUS  INVALID
          │        │         │
          ▼        ▼         ▼
       UPDATE   CLARIFY    REJECT
        STATE    USER       USER
          │
          ▼
       MONGODB (Persisted State & Statuses)
          │
          ▼
   FIND NEXT REQUIRED FIELD (Interview Controller)
          │
          ▼
   GENERATE NEXT QUESTION (Gemini Phrasing / Fallback Map)
          │
          ▼
       FRONTEND
```

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, React Router v6, Tailwind CSS, Lucide Icons, Axios
- **Backend**: Python 3.9+, FastAPI, `google-genai` SDK, Pydantic v2, Pydantic Settings, Motor (async MongoDB driver), Uvicorn, HTTPX
- **Database**: MongoDB (Local instance running on `mongodb://localhost:27017`)
- **LLM**: Google Gemini API (`gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-2.5-flash`)
- **Testing**: Pytest, Pytest-AsyncIO (20 automated unit, integration, and Gemini extraction tests)

---

## 📋 Configuration & Environment Variables

### Backend Configuration (`backend/.env`)

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=document_intake_assistant

# LLM Configuration
LLM_PROVIDER=gemini
USE_MOCK_LLM=false
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite

# CORS & Server
FRONTEND_URL=http://localhost:5173
HOST=0.0.0.0
PORT=8000
```

> **Security Note:** `GEMINI_API_KEY` exists strictly on the backend and is never exposed to the frontend or browser. `.env` is ignored by git; use `.env.example` as a template.

### Frontend Configuration (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Quick Start Guide

### 1. Start MongoDB
Ensure MongoDB is running locally on port 27017:
```powershell
# Windows PowerShell test
Test-NetConnection -ComputerName 127.0.0.1 -Port 27017
```

### 2. Backend Setup
```bash
cd backend

# Activate virtual environment
.\venv\Scripts\activate   # Windows (or: source venv/bin/activate on Unix)

# Install dependencies
pip install -r requirements.txt

# Configure your GEMINI_API_KEY in backend/.env
# Run backend server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend API will be live at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies (if first time)
npm install

# Start Vite dev server
npm run dev
```

The frontend will be live at `http://127.0.0.1:5173`.

---

## 🧪 Automated Testing

The project includes 20 comprehensive automated tests:

```bash
cd backend
.\venv\Scripts\activate

# Run all unit and service tests
pytest -v tests/test_api_endpoints.py tests/test_contradiction_service.py tests/test_document_service.py tests/test_mock_llm.py tests/test_validation_service.py

# Run live Gemini API extraction tests
pytest -v tests/test_gemini_extraction.py
```

### Test Coverage Highlights:
- **`test_gemini_multi_field_extraction`**: Verifies Gemini extracts full name, address, children boolean, and executor with relationship from a single turn.
- **`test_gemini_irrelevant_input_rejection`**: Verifies irrelevant input (*"My favorite color is blue"*) is rejected without polluting state.
- **`test_gemini_ambiguous_input_detection`**: Verifies ambiguous input (*"Maybe I'll have children in the future"*) is flagged as `AMBIGUOUS`.
- **`test_gemini_specific_gifts_extraction`**: Verifies multiple gifts are decomposed into structured items, recipients, and relationships.
- **`test_gemini_all_in_one_message`**: Verifies all fields are populated and verified when provided together.
- **`test_session_lifecycle`**: Verifies full conversational intake turn lifecycle, state persistence, PATCH updates, and document generation.
