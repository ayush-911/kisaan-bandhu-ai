import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

# Dummy training dataset (for hackathon)
# Features: [temp, rain, wind]
X = []
y_growth = []

for _ in range(2000):
    temp = np.random.uniform(10, 45)
    rain = np.random.uniform(0, 120)
    wind = np.random.uniform(0, 18)

    # Create synthetic “growth score”
    score = 100

    # penalize temp extremes
    if temp < 18: score -= (18-temp)*4
    if temp > 32: score -= (temp-32)*4

    # penalize too much rain
    if rain > 60: score -= (rain-60)*1.5

    # penalize too much wind
    if wind > 10: score -= (wind-10)*3

    score = max(0, min(100, score))

    X.append([temp, rain, wind])
    y_growth.append(score)

X = np.array(X)
y_growth = np.array(y_growth)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y_growth)

joblib.dump(model, "kisan_growth_model.pkl")
print("✅ AI Model saved as kisan_growth_model.pkl")
