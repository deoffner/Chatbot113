# Proofline

A simple, hint-first college math tutor that runs entirely in the browser. Proofline responds to common calculus, algebra, linear algebra, and probability prompts with a first hint, then lets students ask for the next step.

## Run locally

1. Set your API key in the current PowerShell session:

	`$env:OPENAI_API_KEY = "your-api-key"`

2. Start the local proxy:

	`python server.py`

3. Open `http://127.0.0.1:8000` in a browser.

Do not put the key in [app.js](app.js) or [index.html](index.html). The browser talks only to the local proxy, which keeps the key server-side. No third-party packages are required.

The tutor instructions live in [server.py](server.py), where you can adjust the teaching style or model configuration.