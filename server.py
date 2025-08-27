# server.py
import os, json, requests
from urllib.parse import unquote
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# --- Env vars ---
JOTFORM_API_KEY  = os.environ.get("JOTFORM_API_KEY", "")
ALLOWED_FORM_IDS = set([s.strip() for s in os.environ.get("ALLOWED_FORM_IDS", "").split(",") if s.strip()])
MCP_NAME         = os.environ.get("MCP_NAME", "jotform")

def jf(url_path, params=None):
    """Call Jotform API with your key."""
    if not JOTFORM_API_KEY:
        raise RuntimeError("JOTFORM_API_KEY env var missing.")
    base = "https://api.jotform.com"
    params = params or {}
    params["apiKey"] = JOTFORM_API_KEY
    r = requests.get(f"{base}{url_path}", params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def check_allowed(form_id: str):
    if ALLOWED_FORM_IDS and form_id not in ALLOWED_FORM_IDS:
        raise RuntimeError(f"Form {form_id} is not in ALLOWED_FORM_IDS")

# ------------- Health -------------
@app.get("/")
def health():
    return f"{MCP_NAME} ok", 200

# ------------- Basic Jotform wrappers -------------
@app.get("/list_forms")
def list_forms():
    data = jf("/user/forms")
    forms = data.get("content", [])
    if ALLOWED_FORM_IDS:
        forms = [f for f in forms if f.get("id") in ALLOWED_FORM_IDS]
    return jsonify({"ok": True, "forms": forms})

@app.get("/get_form/<form_id>")
def get_form(form_id):
    check_allowed(form_id)
    data = jf(f"/form/{form_id}")
    return jsonify({"ok": True, "form": data.get("content")})

@app.get("/list_questions/<form_id>")
def list_questions(form_id):
    check_allowed(form_id)
    data = jf(f"/form/{form_id}/questions")
    return jsonify({"ok": True, "questions": data.get("content", {})})

@app.get("/list_submissions/<form_id>")
def list_submissions(form_id):
    check_allowed(form_id)
    since = request.args.get("since")
    params = {}
    if since:
        params["filter"] = json.dumps({"created_at:gt": since})
    data = jf(f"/form/{form_id}/submissions", params=params)
    return jsonify({"ok": True, "submissions": data.get("content", [])})

@app.get("/get_submission/<submission_id>")
def get_submission(submission_id):
    data = jf(f"/submission/{submission_id}")
    return jsonify({"ok": True, "submission": data.get("content")})

@app.get("/download_file")
def download_file():
    # Use ?url=<encoded public file url>
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "missing url"}), 400
    url = unquote(url).strip().strip("<>").strip("'\"")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return Response(r.content, status=200, headers={
        "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
    })

# ------------- Submit/edit (optional) -------------
@app.post("/create_submission/<form_id>")
def create_submission(form_id):
    check_allowed(form_id)
    body = request.get_json(force=True) or {}
    payload = body.get("payload", {})
    if not payload:
        return jsonify({"ok": False, "error": "missing payload"}), 400
    url = f"https://api.jotform.com/form/{form_id}/submissions"
    payload["apiKey"] = JOTFORM_API_KEY
    r = requests.post(url, data=payload, timeout=90)
    try:
        r.raise_for_status()
    except Exception:
        return jsonify({"ok": False, "status": r.status_code, "body": r.text[:400]}), 400
    return jsonify({"ok": True, "content": r.json().get("content")})

@app.post("/edit_submission/<submission_id>")
def edit_submission(submission_id):
    body = request.get_json(force=True) or {}
    payload = body.get("payload", {})
    if not payload:
        return jsonify({"ok": False, "error": "missing payload"}), 400
    url = f"https://api.jotform.com/submission/{submission_id}"
    payload["apiKey"] = JOTFORM_API_KEY
    r = requests.post(url, data=payload, timeout=90)
    try:
        r.raise_for_status()
    except Exception:
        return jsonify({"ok": False, "status": r.status_code, "body": r.text[:400]}), 400
    return jsonify({"ok": True, "content": r.json().get("content")})

# ------------- Normalize to fields.json-style -------------
def normalize_type(jf_type: str):
    t = jf_type or ""
    if t == "control_fullname": return "full_name"
    if t == "control_address":  return "address"
    if t == "control_phone":    return "phone"
    if t == "control_datetime": return "date"
    if t in ("control_number","control_spinner"): return "number"
    if t in ("control_radio","control_dropdown","control_checkbox"): return "enum"
    return "string"

@app.get("/catalog/<form_id>")
def catalog(form_id):
    check_allowed(form_id)
    qs = jf(f"/form/{form_id}/questions").get("content", {})
    out = []
    for qid, q in qs.items():
        jf_type = q.get("type", "")
        uniq    = q.get("name", "")
        label   = q.get("text") or uniq
        props   = q.get("properties") or {}
        enum = None
        if normalize_type(jf_type) == "enum":
            opts = props.get("options")
            if isinstance(opts, str):
                enum = [o.strip() for o in opts.split("|") if o.strip()]
            elif isinstance(opts, list):
                enum = [str(o).strip() for o in opts if str(o).strip()]
        out.append({
            "qid": str(qid),
            "key": uniq,
            "label": label,
            "jf_type": jf_type,
            "type": normalize_type(jf_type),
            "enum": enum
        })
    return jsonify({"ok": True, "fields": out})

if __name__ == "__main__":
    # Render will set PORT for you; default to 8080 locally
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
