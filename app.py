import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

API_BASE = os.environ.get("API_BASE", "https://speval.tokenengine.ai/api/funnel")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    email = request.form.get("email_address", "").strip()
    language = request.form.get("language", "en")
    file = request.files.get("file")

    if not email or "@" not in email:
        return jsonify({"error": "A valid email address is required."}), 400
    if not file or file.filename == "":
        return jsonify({"error": "Please upload a termsheet file."}), 400

    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or ""
    ip = ip.split(",")[0].strip()

    try:
        resp = requests.post(
            f"{API_BASE}/run_job",
            files={"file": (file.filename, file.stream, file.content_type)},
            data={
                "email_address": email,
                "ip_address": ip,
                "language": language,
                "source_app": "render",
            },
            timeout=60,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to the analysis service."}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
