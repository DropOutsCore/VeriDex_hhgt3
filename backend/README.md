# VERIDEX Backend Service

The backend module of VERIDEX provides FastAPI endpoints for image evidence processing, face detection & embedding matching, reverse image search candidate discovery, cryptographic fingerprinting, and Polygon Amoy blockchain verification.

## Technology Stack
- **Framework**: FastAPI (Python)
- **ASGI Server**: Uvicorn
- **Computer Vision & ML**: OpenCV (YuNet, SFace), NumPy, Pillow, ImageHash
- **HTTP Client**: HTTPX
- **Blockchain**: Web3.py
- **Testing**: Pytest

## Directory Structure

```
backend/
├── app/
│   ├── api/        # Endpoint routes
│   ├── services/   # Processing engines & external integrations
│   ├── models/     # Pydantic data schemas
│   └── utils/      # Shared utilities & cryptographic functions
│   ├── __init__.py
│   └── main.py     # FastAPI application entry point
├── tests/          # Test suite
├── requirements.txt# Python package requirements
└── README.md       # Setup & execution instructions
```

## Quick Start & Execution Commands

### 1. Create & Activate Virtual Environment

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Development Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 4. Run Test Suite

```bash
pytest
```
