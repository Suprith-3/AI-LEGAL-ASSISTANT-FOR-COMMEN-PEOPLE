LegalEase AI — local setup

This small project uses Google Gemini (GenAI) via the `google-genai` SDK and expects an API key in the `GEMINI_API_KEY` environment variable.

Quick setup

1. Install the Python SDK (if you haven't already):

```powershell
# Use your Python environment's pip
python -m pip install --upgrade google-genai
```

2. Create a local `.env` file from the example (for local development):

```powershell
# In the project folder
Copy-Item .\.env.example .\.env
# Edit .env and replace the placeholder
notepad .\.env
```

3. Load `.env` into your current PowerShell session (the repository includes `load_env.ps1`):

```powershell
# Allow the script if blocked (one-time):
Unblock-File .\load_env.ps1
# Run the loader which sets environment variables in this session
.\load_env.ps1; Load-DotEnv
# Confirm variable is set
echo $env:GEMINI_API_KEY
```

4. Alternatively, set the key for the current session manually:

```powershell
$env:GEMINI_API_KEY = 'your_real_gemini_api_key_here'
python .\app.py
```

5. Or persist the variable for your user (new sessions):

```powershell
setx GEMINI_API_KEY "your_real_gemini_api_key_here"
# Close and re-open PowerShell to access the new variable
```

Run the app

```powershell
python .\app.py
```

Security notes

- Never commit your real `.env` or secrets to source control. Add `.env` to .gitignore.
- For production, use a secret manager or environment configuration outside the repo.

If you see an import error for the SDK, run the pip command above.

Run the web app (recommended)

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Start the server (this serves `index.html` and an API endpoint):

```powershell
python .\app.py
```

3. Open your browser to http://127.0.0.1:5000

Notes on API keys and security

- It's safer to keep `GEMINI_API_KEY` on the server (use the steps above to set it in your PowerShell session or in `.env`). The web UI allows you to paste a key for ad-hoc testing, but avoid pasting real production keys into a browser in shared environments.
- Mock mode: set `LEG_MODE=mock` in your environment to run the app without calling Gemini (useful for offline testing):

```powershell
$env:LEG_MODE = 'mock'
python .\app.py
```

If you'd like a CLI flag instead of an environment variable for mock mode, I can add that.