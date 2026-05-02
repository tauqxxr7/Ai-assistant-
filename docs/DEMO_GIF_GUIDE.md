# Demo GIF Guide

Use a real local run or a real deployment. Do not create a mock GIF.

## Goal

Record a 30-second demo that proves the assistant can stream, show verification output, and expose memory controls.

## Recommended Tools

- ScreenToGif on Windows
- OBS
- Browser recording extension

## Setup

Start the backend in PowerShell:

```powershell
Copy .env.example .env
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Start the frontend in another PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Exact 30-Second Flow

1. Open the app and show the chat UI.
2. Ask a live factual question, such as "What are the latest updates on openai.com?"
3. Show the streaming response and status indicator.
4. Show verification details, confidence, and sources if API keys are configured.
5. Ask "Remember that I prefer concise answers" and show the memory sidebar.

If API keys are not configured, the GIF should honestly show the demo-mode message instead of fake citations.

## Output

Save the final GIF as:

```text
screenshots/demo.gif
```
