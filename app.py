import os
import sys
import logging
from typing import Optional

from flask import Flask, request, jsonify, send_from_directory


def load_dotenv_file(path: str = ".env") -> None:
    """
    Lightweight .env loader (no external dependency).
    Reads KEY=VALUE lines and sets them into os.environ for the current process.
    """
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            # skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue
  
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            # remove optional surrounding quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]

            # Only set if not already set in environment
            if key and key not in os.environ:
                os.environ[key] = val



def initialize_gemini_client():
    """
    Initializes the Gemini client by securely reading the API key 
    from the environment variable GEMINI_API_KEY.
    """
    # 1. Read the API key from the environment variable
    # This is the safest way to handle secrets in a backend application.
    # Backwards-compatible initializer kept for scripts that call it directly.
    return get_gemini_client()


def get_gemini_client(api_key: Optional[str] = None):
    """
    Return an initialized genai.Client. If `api_key` is provided it will be used;
    otherwise the function attempts to load GEMINI_API_KEY from the environment (and .env).
    """
    # If caller passed a key use it, otherwise try environment and .env
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            load_dotenv_file(".env")
            api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Set it in your environment or create a .env file with GEMINI_API_KEY=..."
        )

    # Import the SDK here so a missing package produces a clear message and doesn't fail earlier
    try:
        from google import genai
        from google.genai.errors import APIError  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Google GenAI SDK not installed or failed to import: {e}")

    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini Client: {e}")


# Configure simple logging for the server
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def summarize_document(client, document_text):
    """
    Sends the document text to the Gemini API for summarization.
    """
    if not client:
        return {"error": "AI client is not initialized."}

    # Define the same system instruction used in your frontend
    system_prompt = """
You are 'LegalEase AI', a helpful legal assistant. Your job is to analyze legal documents and explain them in simple, plain English (around an 8th-grade reading level). Use Markdown for formatting your response (e.g., "## Summary", "## Complex Terms", "* Item 1").

Your response MUST include three sections:
1.  **## Plain-English Summary:** A brief summary of the document's main purpose and key points.
2.  **## Legal Jargon Explained:** Identify and define complex legal terms from the document in a simple, easy-to-understand way. List them as bullet points.
3.  **## General Suggestions:** Provide a list of general, common-sense next steps or things to consider based on the document's content.

IMPORTANT: You must never provide specific legal advice, recommend a specific lawyer, or create a client-attorney relationship. Always include this disclaimer at the end of your response, exactly as written:
'Disclaimer: I am an AI assistant and not a lawyer. This analysis is for informational purposes only and is not legal advice. You should consult with a qualified legal professional for advice on your specific situation.'
"""

    prompt = f"""
Here is the legal document text:
---
{document_text}
---
Please analyze it according to your instructions.
"""
    
    # Check for mock mode
    if os.environ.get("LEG_MODE", "") == "mock":
        # Return a simple canned response for local testing without network calls
        mocked = (
            "## Plain-English Summary:\nThis is a mock summary used in mock mode.\n\n"
            "## Legal Jargon Explained:\n* MockTerm - A mocked definition.\n\n"
            "## General Suggestions:\n* Review the document with a qualified lawyer.\n\n"
            "Disclaimer: I am an AI assistant and not a lawyer. This analysis is for informational purposes only and is not legal advice. You should consult with a qualified legal professional for advice on your specific situation."
        )
        return {"summary": mocked}

    try:
        from google import genai
        from google.genai.errors import APIError  # type: ignore

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        # Return the AI's generated text
        return {"summary": response.text}

    except APIError as e:
        return {"error": f"Gemini API Error: {e.message}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# --- Flask web server ---
app = Flask(__name__, static_folder='.', static_url_path='')

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "mode": "mock" if os.environ.get('LEG_MODE') == 'mock' else "live"
    })

@app.route('/')
def index():
    # Serve the static index.html from the project root
    return send_from_directory('.', 'index.html')


@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """
    Expects JSON: { "text": "...extracted pdf text...", "apiKey": "optional_client_key" }
    If apiKey is provided it will be used for this request; otherwise the server uses GEMINI_API_KEY.
    """
    print("\n=== Received /api/summarize request ===")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return jsonify({'error': 'Invalid JSON in request body'}), 400
        
    if not data or 'text' not in data:
        print("Error: Missing 'text' in request body")
        return jsonify({'error': 'Missing "text" in request body.'}), 400
        
    print(f"Received text length: {len(data['text'])} chars")
    print(f"Text preview: {data['text'][:200]}...")

    text = data['text']
    api_key = data.get('apiKey')

    # Log a short preview for debugging (do not log full documents in production)
    try:
        preview = (text[:200].replace('\n', ' ')) if isinstance(text, str) else ''
        logging.info(f"POST /api/summarize received: text_length={len(text) if isinstance(text, str) else 'N/A'} apiKey_provided={bool(api_key)} preview='{preview}'")
    except Exception:
        logging.info("POST /api/summarize received (failed to create preview)")

    # Mock mode support
    if os.environ.get('LEG_MODE', '') == 'mock':
        return jsonify(summarize_document(None, text))

    try:
        client = get_gemini_client(api_key=api_key)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    result = summarize_document(client, text)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health endpoint to confirm the app is running."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Helpful startup message
    # Load .env if present for local dev
    load_dotenv_file('.env')

    # Allow starting in mock mode with a simple CLI flag: `python app.py --mock`
    if '--mock' in sys.argv:
        os.environ['LEG_MODE'] = 'mock'
        logging.info('Starting in MOCK mode (LEG_MODE=mock)')
    else:
        logging.info(f"LEG_MODE={os.environ.get('LEG_MODE','')} GEMINI_API_KEY_set={'GEMINI_API_KEY' in os.environ}")

    print('Starting LegalEase AI server on http://127.0.0.1:5000')
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)