def clamp(x, a=0, b=100):
    return max(a, min(b, x))

def growth_probability(temp, rain, ideal_temp, ideal_rain):
    """
    Returns a probability score 0-100 based on matching ideal ranges.
    """
    tmin, tmax = ideal_temp
    rmin, rmax = ideal_rain

    temp_score = 100
    rain_score = 100

    if temp < tmin:
        temp_score -= (tmin - temp) * 6
    elif temp > tmax:
        temp_score -= (temp - tmax) * 6

    if rain < rmin:
        rain_score -= (rmin - rain) * 2
    elif rain > rmax:
        rain_score -= (rain - rmax) * 2

    final_score = (temp_score * 0.65) + (rain_score * 0.35)
    return clamp(int(final_score))

def risk_probabilities(temp, wind_speed, rain_mm):
    """
    Risk probabilities based on thresholds.
    """
    rain_risk = 0
    wind_risk = 0
    heat_risk = 0

    # Rain risk
    if rain_mm > 60:
        rain_risk = 75
    elif rain_mm > 30:
        rain_risk = 50
    elif rain_mm > 10:
        rain_risk = 25

    # Wind risk
    if wind_speed > 12:
        wind_risk = 70
    elif wind_speed > 8:
        wind_risk = 45
    elif wind_speed > 5:
        wind_risk = 20

    # Heat risk
    if temp >= 40:
        heat_risk = 85
    elif temp >= 35:
        heat_risk = 60
    elif temp >= 30:
        heat_risk = 30

    return {
        "rain_damage": rain_risk,
        "wind_damage": wind_risk,
        "heat_stress": heat_risk
    }

def solutions_for_risks(risks):
    solutions = []

    if risks["rain_damage"] >= 50:
        solutions.append("✅ Rain Protection: Make proper drainage & stop irrigation. Spray anti-fungal if needed.")
    if risks["wind_damage"] >= 45:
        solutions.append("✅ Wind Protection: Provide crop support (sticks/net). Avoid pesticide spray during strong wind.")
    if risks["heat_stress"] >= 60:
        solutions.append("✅ Heat Protection: Use mulching, water early morning/evening, avoid noon irrigation.")

    if not solutions:
        solutions.append("✅ Weather looks safe today. Continue normal crop care.")

    return solutions
