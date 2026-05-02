# Screenshot Guide

Use real local runs or real deployments only. Do not add mock screenshots or invented URLs.

## Local Run Steps

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

## Screenshots to Capture

Save screenshots under a `screenshots/` folder with these exact filenames:

- `screenshots/chat-ui.png`: initial chat interface with the memory sidebar visible.
- `screenshots/streaming-answer.png`: an answer mid-stream or immediately after streaming completes, with the status indicator visible.
- `screenshots/memory-page.png`: memory sidebar after saving a preference such as "Remember that I prefer concise answers."
- `screenshots/verification-output.png`: final answer showing confidence, verified items, unverified items, and source citations if API keys are configured.

## Suggested Capture Flow

1. Ask: "Remember that I prefer concise answers."
2. Capture `screenshots/memory-page.png` after the memory appears.
3. Ask: "What are the latest updates on openai.com?"
4. Capture `screenshots/streaming-answer.png` while the status indicator says thinking, searching, verifying, or while tokens are appearing.
5. Capture `screenshots/verification-output.png` after the answer completes.
6. Capture `screenshots/chat-ui.png` from the clean interface or after refreshing.

If API keys are not configured, the verification screenshot should honestly show the demo-mode message instead of fake live citations.
