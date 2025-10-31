Deployment Options
==================

This project can be deployed in several ways. Pick the one that best fits your needs.

1) Render (recommended for simplicity)
-------------------------------------
- Create an account on https://render.com
- Create a new "Web Service" and connect your GitHub repo
- Choose the `main` branch
- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Set environment variables in the Render dashboard (e.g., `GEMINI_API_KEY`, `LEG_MODE` if needed)

Notes: Render will auto-deploy on each push. Use the dashboard to view logs and environment variables.

2) Railway
----------
- Create an account on https://railway.app
- New Project -> Deploy from GitHub
- Select repository and branch
- Set environment variables (GEMINI_API_KEY)
- Set start command to `python app.py`

3) Heroku (classic; requires Procfile)
-------------------------------------
- Install the Heroku CLI and log in
- Create a new Heroku app:
  ```bash
  heroku create my-legal-ease-app
  heroku git:remote -a my-legal-ease-app
  git push heroku main
  ```
- Set config var:
  ```bash
  heroku config:set GEMINI_API_KEY="your_key_here"
  ```

4) Docker (any host that runs Docker)
-------------------------------------
- Build locally:
  ```bash
  docker build -t legal-ease-ai .
  docker run -p 5000:5000 -e GEMINI_API_KEY="your_key_here" legal-ease-ai
  ```
- For production, push the image to Docker Hub or a container registry and use your cloud provider.

5) Azure App Service
--------------------
- Create a Web App for Containers or a Python Web App
- Configure deployment from GitHub
- Set environment variables in Azure Portal (Application settings)

Tips
----
- NEVER commit your real `GEMINI_API_KEY` to GitHub. Use environment variables or a secret manager.
- For local testing without the Gemini network calls, run: `python app.py --mock` or set `LEG_MODE=mock`.
- Enable logging in your host (Render, Railway, Heroku) to see backend logs and troubleshooting info.

Example: GitHub -> Render Auto-deploy
------------------------------------
1. Connect Render to GitHub and authorize the repo
2. Create Web Service and set the build/start commands
3. In the Render dashboard go to "Environment" and add `GEMINI_API_KEY` as a secret
4. Push to `main` and Render will build & deploy automatically

Advanced: GitHub Actions -> Deploy to Render using API
------------------------------------------------------
Render supports direct GitHub integration; for more control you can use a deploy action or call the Render API from a custom workflow. See Render docs for details.

