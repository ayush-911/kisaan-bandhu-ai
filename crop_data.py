CROP_DATABASE = {
    "wheat": {
        "name": "Wheat",
        "ideal_temp": (18, 26),
        "ideal_rain_mm": (20, 60),
        "duration_days": (100, 130),
        "seed_per_acre_kg": 40,
        "fertilizer_plan": [
            "DAP: 50 kg (at sowing)",
            "Urea: 50 kg (after 25-30 days)",
            "Urea: 25 kg (after 50-55 days)"
        ],
        "irrigation_plan": [
            "1st irrigation: 20-25 days",
            "2nd irrigation: 40-45 days",
            "3rd irrigation: 60-65 days",
            "4th irrigation: 80-85 days"
        ]
    },

    "rice": {
        "name": "Rice",
        "ideal_temp": (20, 35),
        "ideal_rain_mm": (80, 200),
        "duration_days": (110, 150),
        "seed_per_acre_kg": 25,
        "fertilizer_plan": [
            "DAP: 40 kg (basal)",
            "Urea: 45 kg (after transplanting 20 days)",
            "Urea: 45 kg (45-50 days)"
        ],
        "irrigation_plan": [
            "Maintain water level 2-5 cm regularly",
            "Drain field 10 days before harvest"
        ]
    },

    "maize": {
        "name": "Maize",
        "ideal_temp": (18, 30),
        "ideal_rain_mm": (40, 100),
        "duration_days": (80, 110),
        "seed_per_acre_kg": 8,
        "fertilizer_plan": [
            "DAP: 50 kg (at sowing)",
            "Urea: 25 kg (30 days)",
            "Urea: 25 kg (55-60 days)"
        ],
        "irrigation_plan": [
            "Irrigate every 10-12 days depending on soil moisture"
        ]
    },

    # ✅ EXTRA CROPS
    "potato": {
        "name": "Potato",
        "ideal_temp": (15, 25),
        "ideal_rain_mm": (20, 80),
        "duration_days": (90, 120),
        "seed_per_acre_kg": 800,
        "fertilizer_plan": [
            "FYM/Compost: 2-3 tons (before sowing)",
            "DAP: 50 kg (basal)",
            "Urea: 40 kg (25 days)",
            "Potash (MOP): 40 kg (30-35 days)"
        ],
        "irrigation_plan": [
            "1st irrigation: 7-10 days after planting",
            "Then every 7-12 days depending on soil moisture",
            "Stop irrigation 7-10 days before harvesting"
        ]
    },

    "tomato": {
        "name": "Tomato",
        "ideal_temp": (18, 30),
        "ideal_rain_mm": (20, 70),
        "duration_days": (80, 120),
        "seed_per_acre_kg": 0.2,
        "fertilizer_plan": [
            "Compost/FYM: 2 tons (before planting)",
            "DAP: 40 kg (basal)",
            "Urea: 20 kg (20-25 days)",
            "Potash (MOP): 25 kg (flowering stage)"
        ],
        "irrigation_plan": [
            "Irrigation every 5-7 days (summer)",
            "Irrigation every 8-10 days (winter)",
            "Avoid waterlogging"
        ]
    },

    "onion": {
        "name": "Onion",
        "ideal_temp": (13, 25),
        "ideal_rain_mm": (20, 60),
        "duration_days": (90, 130),
        "seed_per_acre_kg": 4,
        "fertilizer_plan": [
            "Compost/FYM: 2 tons (before sowing)",
            "DAP: 40 kg (basal)",
            "Urea: 30 kg (30 days)",
            "Potash (MOP): 25 kg (45 days)"
        ],
        "irrigation_plan": [
            "Light irrigation after transplanting",
            "Then every 7-10 days depending on soil moisture",
            "Stop irrigation 10 days before harvesting"
        ]
    },

    "mustard": {
        "name": "Mustard",
        "ideal_temp": (10, 25),
        "ideal_rain_mm": (15, 50),
        "duration_days": (90, 120),
        "seed_per_acre_kg": 2,
        "fertilizer_plan": [
            "DAP: 30 kg (basal)",
            "Urea: 25 kg (30 days)"
        ],
        "irrigation_plan": [
            "1st irrigation: 25-30 days",
            "2nd irrigation: flowering stage"
        ]
    },

    "cotton": {
        "name": "Cotton",
        "ideal_temp": (20, 35),
        "ideal_rain_mm": (40, 100),
        "duration_days": (150, 180),
        "seed_per_acre_kg": 2,
        "fertilizer_plan": [
            "Compost/FYM: 2 tons (before sowing)",
            "DAP: 50 kg (basal)",
            "Urea: 50 kg (30 days)",
            "Urea: 25 kg (60 days)"
        ],
        "irrigation_plan": [
            "Irrigation every 10-15 days (depends on soil)",
            "Avoid excess watering during flowering"
        ]
    },

    "sugarcane": {
        "name": "Sugarcane",
        "ideal_temp": (20, 38),
        "ideal_rain_mm": (60, 200),
        "duration_days": (300, 450),
        "seed_per_acre_kg": 1200,
        "fertilizer_plan": [
            "FYM/Compost: 4 tons (before planting)",
            "DAP: 80 kg (basal)",
            "Urea: 70 kg (45 days)",
            "Urea: 70 kg (90 days)"
        ],
        "irrigation_plan": [
            "Irrigate every 7-10 days in summer",
            "Irrigate every 12-15 days in winter",
            "Ensure drainage during heavy rain"
        ]
    },

    "pulses": {
        "name": "Pulses",
        "ideal_temp": (18, 32),
        "ideal_rain_mm": (20, 80),
        "duration_days": (70, 120),
        "seed_per_acre_kg": 20,
        "fertilizer_plan": [
            "DAP: 30 kg (basal)",
            "Rhizobium culture treatment (recommended)"
        ],
        "irrigation_plan": [
            "Irrigation at flowering stage",
            "Avoid excess watering"
        ]
    }
}
