# Cprice

Cprice is a price-comparison web app for online shopping in India.

## What it does

- Search for a product such as `iPhone 15`
- Fetch live product listings from the configured price provider
- Sort returned offers from lowest price to highest
- Highlight the lowest listed offer
- Open the product/store link directly
- Cache repeated searches briefly to reduce API usage
- Responsive premium dark UI for desktop and mobile

## Stack

- Flask
- Requests
- Flask-CORS
- Gunicorn
- HTML/CSS/JavaScript

## Environment variables

Set these on your hosting provider. Do **not** commit secrets to GitHub.

```text
AMAZON_API_KEY=your_api_key_here
SEARCH_CACHE_TTL=60
PORT=5000
```

## Run locally

```bash
pip install -r requirements.txt
export AMAZON_API_KEY="your_api_key_here"
python app.py
```

Then open `http://localhost:5000`.

## Important

The current provider integration supplies the live data source configured in `app.py`. Cprice's frontend is designed around a normalized offer list, so additional marketplaces can be added as separate provider adapters without rebuilding the UI.

Founder: **Aditya Rajput**  
Developer: **Pradeep Rajput**
