import numpy as np
import joblib
import os

MODEL_PATH = "kisan_growth_model.pkl"

def train_and_save_if_missing():
    """
    If model doesn't exist, train a simple RandomForest model and save it.
    This makes your project 'AI based' and still works offline.
    """
    if os.path.exists(MODEL_PATH):
        return

    from sklearn.ensemble import RandomForestRegressor

    X = []
    y = []

    # Synthetic training data
    for _ in range(2500):
        temp = np.random.uniform(10, 45)
        rain = np.random.uniform(0, 120)
        wind = np.random.uniform(0, 18)

        score = 100

        # temp sweet zone 20-30
        if temp < 20:
            score -= (20 - temp) * 4
        if temp > 30:
            score -= (temp - 30) * 4

        # rain sweet zone 5-40
        if rain < 5:
            score -= (5 - rain) * 1.5
        if rain > 40:
            score -= (rain - 40) * 1.8

        # wind sweet zone < 8
        if wind > 8:
            score -= (wind - 8) * 4

        score = max(0, min(100, score))

        X.append([temp, rain, wind])
        y.append(score)

    model = RandomForestRegressor(n_estimators=250, random_state=42)
    model.fit(np.array(X), np.array(y))

    joblib.dump(model, MODEL_PATH)


def ai_predict(temp, rain_mm, wind_ms):
    """
    Returns:
    growth_probability (0-100),
    rain_risk (0-100),
    wind_risk (0-100),
    heat_risk (0-100)
    """
    train_and_save_if_missing()
    model = joblib.load(MODEL_PATH)

    wind_kmh = wind_ms * 3.6

    X = np.array([[temp, rain_mm, wind_kmh]])
    growth = int(model.predict(X)[0])
    growth = max(0, min(100, growth))

    # Risk probabilities (AI-style)
    # Rain risk
    rain_risk = int(min(100, (rain_mm / 60) * 100)) if rain_mm > 0 else 0

    # Wind risk (km/h)
    wind_risk = int(min(100, (wind_kmh / 30) * 100))

    # Heat risk
    if temp <= 28:
        heat_risk = 10
    elif temp <= 35:
        heat_risk = 45
    elif temp <= 40:
        heat_risk = 70
    else:
        heat_risk = 90

    return growth, rain_risk, wind_risk, heat_risk
