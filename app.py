from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import requests

app = Flask(__name__)
CORS(app)

API_URL = "https://api.amazonscraperapi.com/api/v1/amazon/search"
API_KEY = os.getenv("AMAZON_API_KEY")

# Small in-memory cache to reduce repeated API calls.
CACHE_TTL = int(os.getenv("SEARCH_CACHE_TTL", "60"))
_cache = {}

def get_cached(key):
    item = _cache.get(key)
    if not item:
        return None
    if time.time() - item["time"] > CACHE_TTL:
        _cache.pop(key, None)
        return None
    return item["data"]

def set_cached(key, data):
    # Keep memory bounded on a small deployment.
    if len(_cache) > 100:
        oldest = min(_cache, key=lambda k: _cache[k]["time"])
        _cache.pop(oldest, None)
    _cache[key] = {"time": time.time(), "data": data}

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "cprice"})

@app.route("/search")
def search():
    query = (request.args.get("q") or "").strip()

    if not query:
        return jsonify({"error": "Product query missing"}), 400

    if len(query) > 160:
        return jsonify({"error": "Search query is too long"}), 400

    if not API_KEY:
        return jsonify({
            "error": "AMAZON_API_KEY is not configured on the server"
        }), 503

    cache_key = query.lower()
    cached = get_cached(cache_key)
    if cached is not None:
        return jsonify(cached)

    try:
        response = requests.get(
            API_URL,
            params={
                "api_key": API_KEY,
                "query": query,
                "domain": "in",
            },
            headers={"Accept": "application/json", "User-Agent": "Cprice/1.0"},
            timeout=20,
        )

        content_type = response.headers.get("content-type", "")
        if response.status_code >= 400:
            return jsonify({
                "error": f"Price provider returned HTTP {response.status_code}"
            }), 502

        if "application/json" not in content_type:
            return jsonify({"error": "Price provider returned an invalid response"}), 502

        data = response.json()
        set_cached(cache_key, data)
        return jsonify(data)

    except requests.Timeout:
        return jsonify({"error": "Price provider timed out. Please try again."}), 504
    except requests.RequestException:
        return jsonify({"error": "Could not reach the price provider."}), 502
    except ValueError:
        return jsonify({"error": "Price provider returned invalid JSON."}), 502

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
