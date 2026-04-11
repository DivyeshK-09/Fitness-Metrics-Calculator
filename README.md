# 🏋️‍♂️ Fitness Metrics Calculator

A research-backed, science-driven fitness metrics web app built with **Streamlit** and **Python**. Calculates BMI, BMR, RMR, TDEE, goal-specific macronutrients, fiber, and daily micronutrient targets — all from peer-reviewed sports nutrition guidelines.

---

## 🌐 Live App

> https://fitness-metrics-calculator-rghstm8.streamlit.app/

---

## ✨ Features

- **BMI** — WHO standard formula with category label (Underweight / Normal / Overweight / Obese)
- **BMR** — Estimated as 90% of RMR (display reference only — not used in any calculations)
- **RMR** — Mifflin-St Jeor (1990), drives all downstream calculations
- **TDEE** — RMR × validated activity multipliers
- **Target Calories** — ±500 kcal surplus/deficit based on goal
- **Macronutrients** — Goal-aware (Gain Mass / Maintain / Lose Fat), activity-scaled, always sums to target calories
  - **Protein** — ISSN-backed g/kg ranges, higher on cut to preserve lean mass, lower on bulk
  - **Fats** — Fixed per activity level (1.0–1.15 g/kg), goal-independent for hormonal stability
  - **Carbs** — Pure caloric remainder, floored at 0g
  - **Fiber** — IOM standard: 14g per 1000 kcal, displayed as subset of carbs
- **Micronutrients** — ICMR-NIN 2020 RDA base values, activity-bumped for Iron, Magnesium, Zinc, B-Vitamins, Vitamin C, D, Potassium and Sodium
- **PDF Report** — Downloadable full report with all metrics, macros, fiber, vitamins and minerals

---

## 🧬 Science & Sources

| Metric  | Formula / Standard                                | Source                                          |
| ------- | ------------------------------------------------- | ----------------------------------------------- |
| BMI     | Weight (kg) / Height (m)²                         | WHO                                             |
| RMR     | Mifflin-St Jeor (1990)                            | Mifflin MD et al.                               |
| BMR     | 90% of RMR                                        | Derived from RMR-BMR physiological relationship |
| TDEE    | RMR × Activity Multiplier                         | Validated activity multipliers (1.2 – 1.975)    |
| Protein | 0.8–2.3 g/kg (goal + activity aware)              | ISSN Position Stand 2017                        |
| Fats    | 1.0–1.15 g/kg (activity-scaled, goal-independent) | Whittaker & Harris 2022, NIH DRI                |
| Carbs   | Caloric remainder                                 | Standard sports nutrition approach              |
| Fiber   | 14g / 1000 kcal                                   | IOM Adequate Intake standard                    |
| Micros  | RDA + activity bumps                              | ICMR-NIN 2020, PMC sports nutrition reviews     |

---

## 🗂️ Project Structure

```
Fitness-Metrics-Calculator/
│
├── app.py            # Streamlit UI — all interface, inputs, outputs
├── main.py           # All formulas, logic, calculations, PDF generation
├── requirements.txt  # Python dependencies
└── README.md
```

**`main.py`** contains:

- Unit conversion (kg, lbs, st, oz → kg | cm, m, ft → cm)
- `calc_bmi` — BMI + category
- `calc_rmr` — RMR (Mifflin-St Jeor) — drives all calculations
- `calc_bmr` — BMR (90% of RMR) — display only
- `calc_mc` — TDEE
- `calc_macros` — Protein, Fats, Carbs
- `calc_fiber` — Daily fiber target
- `calc_micros` — Daily vitamin and mineral targets
- `generate_pdf` — Full PDF report generation

**`app.py`** contains:

- Streamlit UI, styling, form inputs
- Results display (BMI, BMR, RMR, TDEE, macros, micros)
- PDF download button

---

## ⚙️ Installation & Running Locally

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/Fitness-Metrics-Calculator.git
cd Fitness-Metrics-Calculator
```

**2. Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
streamlit run app.py
```

**5. Open in browser**

```
http://localhost:8501
```

---

## 📦 Requirements

```
streamlit
fpdf
```

---

## 📋 Supported Input Units

| Measurement | Supported Units                            |
| ----------- | ------------------------------------------ |
| Weight      | kg, lbs, stones (st), ounces (oz)          |
| Height      | cm, meters (m), feet+inches (ft) e.g. 5'11 |
| Age         | Years                                      |

All inputs are converted to **kg** and **cm** before any formula is applied.

---

## 🎯 Goals Supported

| Goal          | Calorie Adjustment | Protein                                 | Fats               | Carbs     |
| ------------- | ------------------ | --------------------------------------- | ------------------ | --------- |
| **GAIN MASS** | TDEE + 500 kcal    | Lower — surplus supports muscle growth  | Fixed per activity | Remainder |
| **MAINTAIN**  | TDEE               | Moderate                                | Fixed per activity | Remainder |
| **LOSE FAT**  | TDEE − 500 kcal    | Higher — preserves lean mass in deficit | Fixed per activity | Remainder |

---

## 🏃‍♂️ Activity Levels

| Level          | Description                                                                | TDEE Multiplier |
| -------------- | -------------------------------------------------------------------------- | --------------- |
| Sedentary      | Little/no exercise, basic household activity                               | 1.2             |
| Lightly Active | Yoga, brisk walking 4–5 kmph (45–60 mins)                                  | 1.375           |
| Moderate       | Casual sports, light weights, jogging (60–90 mins)                         | 1.55            |
| Active         | Weight training, calisthenics, competitive sports (120–150 mins, 3–5 days) | 1.725           |
| Very Active    | Intense training, high-volume workouts (150+ mins, 6–7 days)               | 1.975           |

---

## 📊 Macro Logic

| Macro       | Approach                                                                                                                                           |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fats**    | Fixed g/kg by activity level — 1.0g/kg (Sedentary–Moderate), 1.1g/kg (Active), 1.15g/kg (Very Active). Goal-independent to protect hormonal health |
| **Protein** | g/kg multiplier varies by both activity level and goal. Cut > Maintain > Bulk at every activity level                                              |
| **Carbs**   | Pure caloric remainder: `(target_cal - protein×4 - fats×9) / 4`                                                                                    |
| **Fiber**   | `target_cal / 1000 × 14g` — scales naturally with calorie intake                                                                                   |

---

## 🔬 Micronutrient Approach

Base values from **ICMR-NIN 2020 RDA**, sex-differentiated. Activity-level bumps applied to:

| Micronutrient      | Reason for bump                                  |
| ------------------ | ------------------------------------------------ |
| Vitamin C          | Oxidative stress from exercise                   |
| Vitamin D          | Indoor training limits sunlight                  |
| Iron               | Sweat loss, high-intensity hemolysis             |
| Magnesium          | Sweat loss, 300+ enzymatic reactions under load  |
| Zinc               | Sweat loss, protein turnover                     |
| B1, B2, B3, B6     | Energy metabolism scales with training intensity |
| Potassium & Sodium | Direct electrolyte sweat losses                  |

All other micros stay at base RDA regardless of activity.

---

## ⚠️ Disclaimer

This app provides **general fitness and nutrition reference information** based on publicly available research and dietary guidelines. It is **not a substitute for professional medical or dietetic advice**. Always consult a qualified healthcare provider before making significant changes to your diet or exercise routine.

---

## 👤 Author

Built and maintained by **Cyber Nakama**
