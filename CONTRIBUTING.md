# Contributing

Thanks for improving Live AI Assistant. Keep changes focused, tested, and honest about what is live versus planned.

## Local Setup

PowerShell backend setup:

```powershell
Copy .env.example .env
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

PowerShell frontend setup:

```powershell
cd frontend
npm install
npm run dev
```

## Checks

Run backend tests:

```powershell
cd backend
pytest
```

Run frontend production build and production dependency audit:

```powershell
cd frontend
npm run build
npm audit --omit=dev
```

## Documentation Rules

- Do not add fake screenshots, fake demos, or invented deployment URLs.
- Keep crawling and verification limitations explicit.
- Do not commit `.env`, local databases, build output, or API keys.
