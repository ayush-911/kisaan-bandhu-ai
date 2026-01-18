@app.route("/market_prices", methods=["POST"])
def market_prices():
    body = request.get_json() or {}

    crop = (body.get("crop", "") or "").strip()
    state = (body.get("state", "") or "").strip()

    if not crop or not state:
        return jsonify({"ok": False, "error": "Crop and State required"}), 400

    crop_title = crop.title()

    # ✅ RapidAPI key check
    if not RAPIDAPI_KEY or "PASTE" in RAPIDAPI_KEY:
        return jsonify({
            "ok": False,
            "error": "RAPIDAPI_KEY missing in .env",
            "fix": "Add RAPIDAPI_KEY=xxxxx in .env and restart server"
        }), 400

    try:
        url = f"https://commodity-prices2.p.rapidapi.com/api/Commodity/{crop_title}"

        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        r = requests.get(url, headers=headers, timeout=20)

        print("\n✅ RapidAPI URL:", url)
        print("✅ RapidAPI Status:", r.status_code)
        print("✅ RapidAPI Text:", r.text[:300])

        if r.status_code != 200:
            return jsonify({
                "ok": False,
                "error": f"RapidAPI failed ({r.status_code})",
                "called_url": url,
                "rapid_text": r.text[:300],
                "hint": "This API works for commodities like Gold/Silver/Crude Oil, NOT Tomato/Wheat."
            }), 400

        api_data = r.json()

        # ✅ Gemini summary (optional)
        ai_summary = None
        if GEMINI_MODEL is not None:
            try:
                prompt = f"""
You are KisanAI. Convert this commodity price data to farmer-friendly summary.

Commodity: {crop_title}
Data:
{api_data}

Rules:
- Output minimum 8 lines
- Use emojis + Hinglish
- Explain in simple words
- Give 1 short suggestion
"""
                resp = GEMINI_MODEL.generate_content(prompt)
                ai_summary = (resp.text or "").strip()
            except Exception as e:
                ai_summary = None
                print("❌ Gemini summary error:", e)

        return jsonify({
            "ok": True,
            "source": "rapidapi",
            "commodity": crop_title,
            "state": state.title(),
            "ai_summary": ai_summary,
            "raw": api_data
        })

    except Exception as e:
        print("❌ RapidAPI Exception:", e)
        return jsonify({
            "ok": False,
            "error": "Server error while calling RapidAPI",
            "debug": str(e)
        }), 500
