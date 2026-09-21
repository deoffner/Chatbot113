# Precalculus Tutor

A simple, hint-first precalculus tutor that runs entirely in the browser. It responds to common algebra, trigonometry, and function questions with a first hint, then lets students ask for the next step.

## Run locally

### 1. Configure the API key

Create a `.env` file in the project folder with:

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

Keep this file private. Do not put the key in [app.js](app.js) or [index.html](index.html), and do not commit it to source control.

### 2. Start the app

From this project folder, run either:

```powershell
python server.py
```

or double-click `start_server.bat`.

The server should display:

```text
Precalculus Tutor running at http://127.0.0.1:8000
```

### 3. Open the tutor

Open this exact address in your browser:

<http://127.0.0.1:8000>

Do not open `index.html` directly or use Five Server. The Python server serves the webpage and the `/api/chat` route together; the browser sends chat requests to that same server.

No third-party packages are required.

### Troubleshooting

- If the page says the tutor is unavailable, confirm that `server.py` is still running.
- If the server reports that `OPENAI_API_KEY` is not configured, check that `.env` is in the same folder as `server.py` and that the variable is spelled exactly as shown above.
- If OpenAI returns an authentication error, revoke the old key and create a new one, then update `.env`.

The tutor instructions live in [server.py](server.py), where you can adjust the teaching style or model configuration.