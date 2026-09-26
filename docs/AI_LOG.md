# AI Development Log

This document records the AI-assisted engineering process, tools employed, architectural iterations, identified defects, and deliberate human-in-the-loop decisions made during the development of the **Document Intake Assistant**.

---

## 1. Tools & Services Used

- **AI Model**: Gemini 3.8 Flash (High) via Antigravity Pair-Programming Agent.
- **Terminal & Shell**: Windows PowerShell 5.1 / 7.
- **Backend Runtime**: Python 3.9.13, FastAPI, Motor, Pydantic v2, Pytest.
- **Frontend Stack**: Node.js v24.11.0, React 18, Vite 8, Tailwind CSS v3.4, Lucide Icons.
- **Database**: Local MongoDB Server on `127.0.0.1:27017` (`document_intake_assistant`).

---

## 2. Key Iterations & Timeline

### Iteration 1: Environment Discovery & Local MongoDB Verification
- **Action**: Queried active Windows services to check for MongoDB availability.
- **Finding**: Detected `MongoDB Server (MongoDB)` already running as an active service listening on TCP port `27017`.
- **Decision**: Configured the application to connect directly to the existing local MongoDB service (`mongodb://localhost:27017/document_intake_assistant`), avoiding unnecessary Docker overhead or mock databases.

### Iteration 2: Pydantic v2 Model Architecture & Field Status Tracking
- **Action**: Created `StructuredState`, `Executor`, `FieldStatus`, and `StateUpdateRequest` models.
- **Iteration**: Added explicit `field_statuses` mapping (`unknown`, `provided`, `confirmed`, `conflicting`) to ensure the frontend can render accurate visual badges (`Provided` vs `Pending`) alongside field values.
- **Decision**: Decoupled `is_complete` and `get_missing_fields()` logic into methods on the model to drive deterministic interview progression.

### Iteration 3: Deterministic Mock LLM vs Real LLM Provider
- **Action**: Designed `BaseLLMService` abstract interface with `OpenAIService` and `MockLLMService`.
- **Iteration**: The mock service was built to be fully deterministic, recognizing:
  1. Sequential questions based on `missing_fields`.
  2. Multi-field extraction (e.g., *"My brother James Smith should be my executor. My name is Jane."*).
  3. Ambiguity triggers (e.g., *"I'm not sure"* -> generates clarification with quick-reply buttons).
  4. Contradictions (e.g., prior `has_children=False` vs new statement mentioning children).
  5. Explicit corrections (e.g., *"Actually, Sarah should be my executor instead of James."*).

### Iteration 4: Reference UI Alignment & Frontend Implementation
- **Action**: Replicated the reference SaaS multi-page layout:
  - Landing Page (`/`): Hero, Trust badges, Feature cards, How it works, primary CTA.
  - Main Intake Page (`/app`): Top 5-step progress bar, collapsible left sidebar, conversational stream with auto-scroll and quick action chips, live structured data side-panel with completion ring.
  - Review Page (`/review`): Grouped cards with edit triggers, "Edit All", and "Continue to Document".
  - Document Preview (`/document`): Legal draft rendering with `DRAFT — FICTIONAL DOCUMENT` watermark, disclaimer, and print-ready PDF styling.

---

## 3. Defects & Bugs Found and Resolved

### Defect 1: Pydantic V2 `.dict()` Deprecation Warnings
- **Symptom**: During initial test execution, Pydantic V2 raised deprecation warnings for `state.dict()`.
- **Fix**: Replaced all `.dict()` calls with `.model_dump()` across `session_service.py`, `state_service.py`, and `routes_state.py`.

### Defect 2: Typing `Tuple` NameError in `mock_llm_service.py`
- **Symptom**: `mock_llm_service.py` used `Tuple[str, List[str]]` in method annotations without importing `Tuple` from `typing`.
- **Fix**: Added `Tuple` to typing imports.

### Defect 3: Pytest-AsyncIO Event Loop Mismatch with Motor Client
- **Symptom**: `RuntimeError: Task ... got Future attached to a different loop` when running tests sequentially.
- **Root Cause**: `setup_test_db` was session-scoped, whereas `pytest-asyncio` creates a new event loop per test by default in Python 3.9. Motor was attached to the initial event loop.
- **Fix**: Changed the database fixture to run per test function on the active event loop, reconnecting cleanly.

### Defect 4: Precedence Bug in `has_children` Validation
- **Symptom**: When `has_children=False` was submitted alongside a raw candidate containing `children: ["Ghost"]`, the child list loop set `cleaned["has_children"] = True`.
- **Fix**: Updated `ValidationService` to enforce that if `has_children` is explicitly `False`, `has_children` remains `False` and `children` is strictly normalized to `[]`.

### Defect 5: Gift String Normalization
- **Symptom**: When user typed *"I want my watch to go to Michael."*, the regex captured *"my watch to go to Michael"*. Section 13/49 UI expected clean normalized formatting *"My watch to Michael"*.
- **Fix**: Added regex normalization converting *"to go to"* into *"to"* and capitalizing the first letter.

---

## 4. Key AI Decisions Evaluated and Corrected

| Initial AI Thought | Critique / Questioning | Final Decision |
|---|---|---|
| Use raw LLM history directly to construct the document draft. | Violates prompt constraint #30. Chat histories often contain corrected or invalid facts. | Built `DocumentService` to generate the HTML and text strictly from the validated `StructuredState` in MongoDB. |
| Use an in-memory dictionary for rapid testing and skip MongoDB. | Prompt explicitly specifies local MongoDB integration (`mongodb://localhost:27017`). | Integrated Motor async client with `sessions`, `conversations`, `structured_states`, and `documents` collections. |
| Use a generic dark-mode chatbot layout. | Prompt section 1 emphasizes preserving the reference multi-page SaaS design with top progress steps, sidebar, and live side-panel. | Faithfully reproduced the blue/navy/indigo rounded-card layout matching the reference mockup. |
