from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print(key)  # should show your key
import time
import urllib.parse
import requests

from flask import Flask, render_template, request, jsonify, send_file

from crop_data import CROP_DATABASE
from risk_engine import solutions_for_risks
from pdf_report import generate_pdf
from ml_model import ai_predict
from translator import translate_text
from gemini_client import ask_gemini


# ✅ Load .env properly
try:
    from dotenv import load_dotenv
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ENV_PATH = os.path.join(BASE_DIR, ".env")
    load_dotenv(ENV_PATH)
    print("✅ .env loaded from:", ENV_PATH)
except Exception as e:
    print("❌ python-dotenv not installed OR .env not found:", e)

app = Flask(__name__)

OPENWEATHER_API_KEY = (os.getenv("OPENWEATHER_API_KEY") or "").strip()

LAST_REPORT_FILE = None

# ✅ Memory per user (for chatbot)
USER_CONTEXT = {}

# ✅ Cache for market (saves Gemini quota)
MARKET_CACHE = {}
CACHE_TTL_SEC = 600  # 10 minutes

# ✅ Nominatim headers (required)
OSM_HEADERS = {
    "User-Agent": "KisanSuperAI/1.0 (route-finder)"
}

# ✅ OFFLINE APPROX MANDI PRICE DATABASE (₹/kg)
OFFLINE_MANDI_RATES = {
    # vegetables
    "onion": (18, 35),
    "potato": (12, 28),
    "tomato": (10, 30),
    "brinjal": (20, 45),
    "ladyfinger": (20, 55),
    "cauliflower": (15, 40),
    "cabbage": (10, 30),
    "chilli": (40, 120),
    "garlic": (90, 220),
    "ginger": (80, 180),

    # grains
    "wheat": (22, 30),
    "rice": (28, 45),
    "maize": (18, 30),
    "mustard": (45, 70),
    "cotton": (55, 85),
    "sugarcane": (3, 6),
    "pulses": (65, 110),

    # fruits
    "banana": (25, 45),
    "apple": (80, 160),
    "mango": (40, 120),
    "orange": (35, 90),
    "grapes": (50, 120),
}

# ✅ small state-based multiplier (optional, keeps it realistic)
STATE_MULTIPLIER = {
    "bihar": 1.00,
    "up": 1.00,
    "uttar pradesh": 1.00,
    "west bengal": 1.03,
    "wb": 1.03,
    "maharashtra": 1.07,
    "mp": 1.02,
    "madhya pradesh": 1.02,
    "punjab": 1.05,
    "haryana": 1.04,
    "rajasthan": 1.01,
    "odisha": 1.02,
    "jharkhand": 1.02,
    "tamil nadu": 1.08,
    "karnataka": 1.06,
    "telangana": 1.06,
    "andhra pradesh": 1.06,
    "gujarat": 1.05,
    "assam": 1.03,
}


# ✅ ---------------- ROUTES (PAGES) ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/predictor")
def predictor():
    return render_template("predict.html")


@app.route("/market")
def market_page():
    return render_template("market.html")


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/disease")
def disease_page():
    return render_template("disease.html")


@app.route("/weather")
def weather_page():
    return render_template("weather.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


# ✅ ---------------- WEATHER FETCH ----------------

def get_weather(location):
    try:
        if not OPENWEATHER_API_KEY:
            return None, "OPENWEATHER_API_KEY missing"

        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        res = requests.get(url, timeout=10)
        data = res.json()

        if "main" not in data:
            return None, data.get("message", "Weather API failed")

        temp = float(data["main"]["temp"])
        wind = float(data.get("wind", {}).get("speed", 0))  # m/s

        rain_mm = 0.0
        if "rain" in data and "1h" in data["rain"]:
            rain_mm = float(data["rain"]["1h"])

        return (temp, wind, rain_mm), None

    except Exception as e:
        return None, str(e)


@app.route("/weather_only", methods=["POST"])
def weather_only():
    body = request.get_json() or {}
    location = (body.get("location") or "").strip()

    if not location:
        return jsonify({"ok": False, "error": "Location required"}), 400

    weather, err = get_weather(location)
    if not weather:
        return jsonify({"ok": False, "error": f"Weather error: {err}"}), 400

    temp, wind, rain_mm = weather

    return jsonify({
        "ok": True,
        "temp": temp,
        "rain": rain_mm,
        "wind_kmh": round(wind * 3.6, 1)
    })


# ✅ ---------------- PREDICT ----------------

@app.route("/predict", methods=["POST"])
def predict():
    global LAST_REPORT_FILE
    body = request.get_json() or {}

    location = (body.get("location") or "").strip()
    crop_key = body.get("crop", "wheat")
    acres = float(body.get("acres", 1))
    lang = body.get("lang", "en")

    if not location:
        return jsonify({"ok": False, "error": translate_text("Please enter location like: Kolkata, IN", lang)}), 400

    crop = CROP_DATABASE.get(crop_key)
    if not crop:
        return jsonify({"ok": False, "error": translate_text("Invalid crop selected", lang)}), 400

    weather, err = get_weather(location)
    if not weather:
        return jsonify({"ok": False, "error": translate_text(f"Weather error: {err}", lang)}), 400

    temp, wind, rain_mm = weather

    prob, rain_risk_ai, wind_risk_ai, heat_risk_ai = ai_predict(temp, rain_mm, wind)

    prob = int(prob)
    rain_risk_ai = int(rain_risk_ai)
    wind_risk_ai = int(wind_risk_ai)
    heat_risk_ai = int(heat_risk_ai)

    risks = {
        "rain_damage": rain_risk_ai,
        "wind_damage": wind_risk_ai,
        "heat_stress": heat_risk_ai
    }

    solutions = solutions_for_risks(risks)

    seed_needed = crop["seed_per_acre_kg"] * acres
    duration_min, duration_max = crop["duration_days"]

    if prob >= 75:
        sowing_msg = "✅ Excellent time to sow in next 2-3 days."
    elif prob >= 55:
        sowing_msg = "⚠️ Moderate time. Sow with precautions."
    else:
        sowing_msg = "❌ Not recommended now. Weather risk is high."

    report_lines = [
        f"Location: {location}",
        f"Crop: {crop['name']}",
        f"Temperature: {temp} °C",
        f"Rain (1h): {rain_mm} mm",
        f"Wind Speed: {wind:.2f} m/s",
        f"AI Growth Probability: {prob}%",
        f"AI Rain Damage Risk: {risks['rain_damage']}%",
        f"AI Wind Damage Risk: {risks['wind_damage']}%",
        f"AI Heat Stress Risk: {risks['heat_stress']}%",
        f"Seed Required: {seed_needed:.1f} kg for {acres} acres",
        f"Duration: {duration_min}-{duration_max} days",
        "Solutions:",
        *solutions
    ]

    LAST_REPORT_FILE = generate_pdf(report_lines)

    return jsonify({
        "ok": True,
        "best_time": translate_text(sowing_msg, lang),
        "probability": prob,
        "summary": translate_text(
            f"Temp: {temp}°C | Rain: {rain_mm}mm | Wind: {wind * 3.6:.1f} km/h",
            lang
        ),
        "rain_risk": risks["rain_damage"],
        "wind_risk": risks["wind_damage"],
        "heat_risk": risks["heat_stress"],
        "solutions": [translate_text(s, lang) for s in solutions],
        "seed_need": translate_text(f"{seed_needed:.1f} kg", lang),
        "duration": translate_text(f"{duration_min}-{duration_max} days", lang),
        "fertilizer_plan": [translate_text(x, lang) for x in crop.get("fertilizer_plan", [])],
        "irrigation_plan": [translate_text(x, lang) for x in crop.get("irrigation_plan", [])]
    })


@app.route("/download_pdf")
def download_pdf():
    global LAST_REPORT_FILE
    if not LAST_REPORT_FILE or not os.path.exists(LAST_REPORT_FILE):
        return "No report generated yet. Click Predict first.", 400
    return send_file(LAST_REPORT_FILE, as_attachment=True)


@app.route("/download_report")
def download_report():
    return download_pdf()


# ✅ ---------------- CHATBOT (ASK CITY + CROP FIRST) ----------------

@app.route("/chat", methods=["POST"])
def chat_ui_route():
    body = request.get_json() or {}
    msg = (body.get("message") or "").strip()
    lang = body.get("lang", "en")
    user_id = body.get("user_id", "default_user")

    if not msg:
        return jsonify(ok=False, error="Empty message"), 400

    ctx = USER_CONTEXT.get(user_id, {"city": None, "crop": None, "waiting_for": None})

    if not ctx.get("city") and ctx.get("waiting_for") is None:
        ctx["waiting_for"] = "city"
        USER_CONTEXT[user_id] = ctx
        return jsonify(ok=True, reply=translate_text("✅ Hi farmer 👋 Apka Gaav/City kya hai?", lang))

    if ctx.get("waiting_for") == "city":
        ctx["city"] = msg
        ctx["waiting_for"] = "crop"
        USER_CONTEXT[user_id] = ctx
        return jsonify(ok=True, reply=translate_text("✅ Nice! Ab aap kaunsa crop ugate ho? (Example: Wheat, Rice, Tomato)", lang))

    if ctx.get("waiting_for") == "crop":
        ctx["crop"] = msg
        ctx["waiting_for"] = None
        USER_CONTEXT[user_id] = ctx
        return jsonify(ok=True, reply=translate_text("✅ Perfect! Ab apna farming question pucho 😄", lang))

    prompt = f"""
You are KisanAI (Indian Agriculture Expert).

Farmer Location (Gaav/City): {ctx.get('city')}
Farmer Crop: {ctx.get('crop')}

Farmer Question: {msg}

Rules:
- Hinglish response
- Bullet points only (no long paragraphs)
- Give step-by-step practical solution
- Include low-cost + organic methods
- If pesticide/spray needed, give exact dose per litre
- Add safety tips
"""

    try:
        reply = ask_gemini(prompt)

        if lang and lang != "en":
            reply = translate_text(reply, lang)

        return jsonify(ok=True, reply=reply)

    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            return jsonify(ok=False, error="429 RESOURCE_EXHAUSTED"), 429
        return jsonify(ok=False, error=err), 500


@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    body = request.get_json() or {}
    user_id = body.get("user_id", "default_user")
    USER_CONTEXT.pop(user_id, None)
    return jsonify(ok=True, msg="Chat reset")


# ✅ ---------------- MARKET PRICES (AI + OFFLINE FALLBACK) ----------------

def normalize_crop_name(text: str) -> str:
    t = (text or "").strip().lower()
    t = t.replace("-", " ").replace("_", " ")
    t = " ".join(t.split())
    return t


def offline_mandi_answer(crop: str, state: str) -> str:
    crop_key = normalize_crop_name(crop)
    state_key = normalize_crop_name(state)

    # try exact match
    rate = OFFLINE_MANDI_RATES.get(crop_key)

    # try partial match: "tomato local" -> "tomato"
    if not rate:
        for k in OFFLINE_MANDI_RATES.keys():
            if k in crop_key:
                rate = OFFLINE_MANDI_RATES[k]
                crop_key = k
                break

    if not rate:
        return f"""⚠️ Approx Market Price (Offline Mode)
✅ Crop: {crop}
✅ State: {state}

❌ Offline price not available for this crop.
✅ Try: Onion, Potato, Tomato, Wheat, Rice, Maize

⚠️ Disclaimer: Please check nearest mandi once ✅"""

    min_kg, max_kg = rate

    # apply multiplier if state known
    mult = STATE_MULTIPLIER.get(state_key, 1.0)
    min_kg = int(round(min_kg * mult))
    max_kg = int(round(max_kg * mult))

    avg_kg = int(round((min_kg + max_kg) / 2))

    min_q = min_kg * 100
    max_q = max_kg * 100
    avg_q = avg_kg * 100

    return f"""⚠️ Approx Market Price (Offline Mode)
✅ Crop: {crop_key.title()}
✅ State: {state.title()}

✅ Min: ₹{min_kg}/kg  |  ₹{min_q}/quintal
✅ Avg: ₹{avg_kg}/kg  |  ₹{avg_q}/quintal
✅ Max: ₹{max_kg}/kg  |  ₹{max_q}/quintal

🔸 Price depends on quality, season, transport, local demand.
✅ Tip: Morning mandi time often gives better selling rates.

⚠️ Disclaimer: Please check nearest mandi once ✅"""


def gemini_market_price(crop: str, state: str) -> str:
    prompt = f"""
You are KisanAI. Generate approximate mandi/market price range for India.

Crop: {crop}
State: {state}

Rules:
- First line: ⚠️ Approx price only, real mandi price may differ
- Minimum 8 lines output
- Give approx range in ₹/kg AND ₹/quintal
- Mention 3 reasons why price changes
- Suggest best selling time
- Add 1 short verification tip
- Hinglish + emojis
- End with: "⚠️ Disclaimer: Please check nearest mandi once ✅"
- Do NOT claim official govt data.

Answer now:
"""
    return ask_gemini(prompt)


@app.route("/market_prices", methods=["POST"])
def market_prices():
    body = request.get_json() or {}
    crop = (body.get("crop") or "").strip()
    state = (body.get("state") or "").strip()

    if not crop or not state:
        return jsonify({"ok": False, "error": "Crop and State required"}), 400

    cache_key = f"{crop.lower()}::{state.lower()}"

    # ✅ return cached response if fresh
    if cache_key in MARKET_CACHE:
        cached = MARKET_CACHE[cache_key]
        if time.time() - cached["time"] < CACHE_TTL_SEC:
            return jsonify({"ok": True, "ai_price": cached["text"]})

    # ✅ try Gemini first
    try:
        ans = gemini_market_price(crop, state)
        MARKET_CACHE[cache_key] = {"time": time.time(), "text": ans}
        return jsonify({"ok": True, "ai_price": ans})

    except Exception as e:
        err = str(e)

        # ✅ If Gemini fails / quota -> use offline fallback (NO ERROR!)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            offline = offline_mandi_answer(crop, state)
            MARKET_CACHE[cache_key] = {"time": time.time(), "text": offline}
            return jsonify({"ok": True, "ai_price": offline})

        # ✅ any other Gemini crash -> still show offline
        offline = offline_mandi_answer(crop, state)
        MARKET_CACHE[cache_key] = {"time": time.time(), "text": offline}
        return jsonify({"ok": True, "ai_price": offline})


# ✅ ---------------- ROUTE ENGINE (FREE) ----------------

def geocode_place(place: str):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers=OSM_HEADERS, timeout=12)
        data = r.json()
        if not data:
            return None, None, "Place not found"
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        name = data[0].get("display_name", place)
        return lat, lon, name
    except Exception as e:
        return None, None, str(e)


def safety_score(distance_km: float, wind_kmh: float, rain_mm: float):
    score = 92
    reasons = []

    if distance_km > 200:
        score -= 18
        reasons.append("Long distance travel (fatigue + fuel + delays).")
    elif distance_km > 80:
        score -= 8
        reasons.append("Medium distance route (expect traffic + stops).")

    if rain_mm >= 5:
        score -= 18
        reasons.append("Rain detected: slippery roads + visibility low.")
    elif rain_mm > 0:
        score -= 8
        reasons.append("Light rain possible: keep speed controlled.")

    if wind_kmh >= 35:
        score -= 12
        reasons.append("High wind: risky for bikes + loaded vehicles.")
    elif wind_kmh >= 20:
        score -= 6
        reasons.append("Moderate wind: be careful on open highways.")

    score = max(35, min(98, score))

    if score >= 80:
        reasons.insert(0, "Overall safe route ✅ Travel normally.")
    elif score >= 60:
        reasons.insert(0, "Moderate risk ⚠️ Travel carefully.")
    else:
        reasons.insert(0, "High risk ❌ Avoid now if possible.")

    return int(score), reasons


@app.route("/route_pro", methods=["POST"])
def route_pro():
    body = request.get_json() or {}
    start = (body.get("start") or "").strip()
    end = (body.get("end") or "").strip()

    if not start or not end:
        return jsonify(ok=False, error="Start and End required"), 400

    s_lat, s_lon, s_err = geocode_place(start)
    if s_lat is None:
        return jsonify(ok=False, error=f"Start not found: {s_err}"), 400

    e_lat, e_lon, e_err = geocode_place(end)
    if e_lat is None:
        return jsonify(ok=False, error=f"End not found: {e_err}"), 400

    try:
        osrm_url = f"https://router.project-osrm.org/route/v1/driving/{s_lon},{s_lat};{e_lon},{e_lat}"
        params = {"overview": "full", "geometries": "geojson"}
        r = requests.get(osrm_url, params=params, timeout=15)
        data = r.json()

        if data.get("code") != "Ok":
            return jsonify(ok=False, error="Routing failed"), 500

        route = data["routes"][0]
        dist_m = float(route["distance"])
        dur_s = float(route["duration"])

        distance_km = dist_m / 1000.0
        duration_min = int(round(dur_s / 60.0))

        distance_text = f"{distance_km:.1f} km"
        duration_text = f"{duration_min} min"

        coords_lonlat = route["geometry"]["coordinates"]
        coords_latlon = [[c[1], c[0]] for c in coords_lonlat]

        w, w_err = get_weather(end)
        wind_kmh = 0
        rain_mm = 0
        if w:
            temp, wind_ms, rain_mm = w
            wind_kmh = wind_ms * 3.6

        safety_percent, safety_reasons = safety_score(distance_km, wind_kmh, rain_mm)

        return jsonify(
            ok=True,
            distance_km=distance_km,
            duration_min=duration_min,
            distance_text=distance_text,
            duration_text=duration_text,
            route_coords=coords_latlon,
            safety_percent=safety_percent,
            safety_reasons=safety_reasons
        )

    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route("/best_route", methods=["POST"])
def best_route():
    body = request.get_json() or {}
    start = (body.get("start") or "").strip()
    end = (body.get("end") or "").strip()

    if not start or not end:
        return jsonify({"ok": False, "error": "Start and End required"}), 400

    directions_url = "https://www.google.com/maps/dir/?api=1" \
        f"&origin={urllib.parse.quote(start)}" \
        f"&destination={urllib.parse.quote(end)}" \
        "&travelmode=driving"

    embed_url = f"https://www.google.com/maps?q={urllib.parse.quote(start)}&output=embed"

    return jsonify({
        "ok": True,
        "directions_url": directions_url,
        "embed_url": embed_url
    })


if __name__ == "__main__":
    app.run(debug=True)
