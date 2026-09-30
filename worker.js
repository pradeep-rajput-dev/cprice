export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response("", { headers: cors() });
    }
    if (url.pathname === "/health") {
      return json({ ok: true, service: "cprice-live-api" });
    }
    if (url.pathname !== "/search") {
      return json({ error: "Not found" }, 404);
    }

    const q = (url.searchParams.get("q") || "").trim();
    if (!q || q.length > 160) return json({ error: "Invalid query" }, 400);
    if (!env.AMAZON_API_KEY) return json({ error: "AMAZON_API_KEY secret is missing" }, 503);

    const cache = caches.default;
    const cacheKey = new Request(
      new URL("/search?q=" + encodeURIComponent(q.toLowerCase()), request.url).toString(),
      { method: "GET" }
    );

    const cached = await cache.match(cacheKey);
    if (cached) return cached;

    const api = new URL("https://api.amazonscraperapi.com/api/v1/amazon/search");
    api.searchParams.set("api_key", env.AMAZON_API_KEY);
    api.searchParams.set("query", q);
    api.searchParams.set("domain", "in");

    try {
      const r = await fetch(api.toString(), {
        headers: { "Accept": "application/json", "User-Agent": "Cprice/1.0" }
      });
      const body = await r.text();
      if (!r.ok) return json({ error: "Price provider HTTP " + r.status }, 502);

      let data;
      try { data = JSON.parse(body); }
      catch { return json({ error: "Price provider returned invalid JSON" }, 502); }

      const response = json(data);
      response.headers.set("Cache-Control", "public, max-age=60");
      await cache.put(cacheKey, response.clone());
      return response;
    } catch {
      return json({ error: "Could not reach price provider" }, 502);
    }
  }
};

function cors() {
  return {
    "Access-Control-Allow-Origin": "https://pradeep-rajput-dev.github.io",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Accept"
  };
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors() }
  });
}
