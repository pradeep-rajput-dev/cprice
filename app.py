from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = "asa_live_0GQLuJ0G3ZlXU8bNgxmouzZulaK2fDHm"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():

    product = request.args.get("q")

    if not product:
        return jsonify({
            "error": "Product query missing"
        }), 400

    url = "https://api.amazonscraperapi.com/api/v1/amazon/search"

    params = {
        "api_key": API_KEY,
        "query": product,
        "domain": "in"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        return jsonify(response.json())

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )