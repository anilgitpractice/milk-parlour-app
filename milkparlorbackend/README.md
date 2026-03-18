## Milk Parlour Backend (FastAPI)

This is a minimal FastAPI backend scaffold for a Milk Parlour management system, focusing on local development with SQLite.

### Features

- **Authentication API**: Register and log in users (mock tokens for now).
- **Subscription API**: Start, pause, and list daily milk subscriptions (in-memory mock).
- **Inventory API**: View current stock levels for different milk types (mock data).
- **AI Chatbot API**: Send a text query and receive a mock AI reply (placeholder for a real LLM).

### Project Structure

- `main.py` – FastAPI application entrypoint and router registration.
- `routers/` – Modular API endpoints:
  - `auth.py`
  - `subscription.py`
  - `inventory.py`
  - `chatbot.py`
- `models/` – Placeholder for SQLAlchemy ORM models.
- `db.py` – SQLite SQLAlchemy engine, base class, and session dependency.
- `requirements.txt` – Python dependencies.

### Setup

1. Create and activate a virtual environment (PowerShell):

   ```powershell
   cd d:\milkparlorbackend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the development server:

   ```powershell
   uvicorn main:app --reload
   ```

4. Open the interactive API docs:

   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

