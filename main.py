from fpdf import FPDF
from io import BytesIO
import re

# --- UNIT CONVERSION ---
# All formulas expect: Weight in kg, Height in cm, Age in years

def convert_weight(W_raw, weight_unit):
    """Convert any weight unit to kg before formula use."""
    if weight_unit == "lbs":
        return W_raw * 0.453592
    elif weight_unit == "st":
        return W_raw * 6.35029
    elif weight_unit == "oz":
        return W_raw * 0.0283495
    else:  # kg
        return W_raw

def convert_height(height_input, height_unit):
    """Convert any height unit to cm before formula use."""
    try:
        if height_unit == "ft":
            match = re.match(r"^\s*(\d+)'(\d*\.?\d*)\s*\"?\s*$", height_input)
            if match:
                ft = float(match.group(1))
                inch = float(match.group(2)) if match.group(2) else 0.0
                return ft * 30.48 + inch * 2.54, None
            else:
                return 0, "❌ Enter height like 5'11 or 6'0.5\""
        elif height_unit == "m":
            return float(height_input) * 100, None
        else:  # cm
            return float(height_input), None
    except:
        return 0, "❌ Invalid height input"


# --- FORMULAS ---
# W = kg, H = cm, A = years, S = "m" or "f"

def calc_bmi(W, H):
    """BMI — WHO standard formula. W in kg, H in cm."""
    return round(W / (H / 100) ** 2, 1)

def get_bmi_category(bmi):
    """Returns WHO BMI category label."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"

def calc_rmr(W, H, A, S):
    """
    Mifflin-St Jeor RMR (1990).
    Drives all downstream calculations: TDEE, macros, fiber, micros.
    W in kg, H in cm, A in years.
    Male:   (10 * W) + (6.25 * H) - (5 * A) + 5
    Female: (10 * W) + (6.25 * H) - (5 * A) - 161
    """
    base = (10 * W) + (6.25 * H) - (5 * A)
    return base + 5 if S.lower() == "m" else base - 161

def calc_bmr(rmr):
    """
    BMR estimated as 90% of RMR (Mifflin-St Jeor).
    BMR is always slightly lower than RMR — the difference accounts
    for the minimal energy cost of being awake and at rest.
    Display only — NOT used for TDEE or any downstream calculations.
    """
    return round(rmr * 0.90)

def calc_mc(rmr, activity_level):
    """
    TDEE — RMR (Mifflin-St Jeor) multiplied by activity factor.
    Activity multipliers validated for use with RMR, not BMR.
    """
    activity = {
        'SEDENTARY 🛌':   1.2,
        'LIGHT 🧘‍♂️':      1.375,
        'MODERATE 🧖‍♂️':   1.555,
        'ACTIVE 🏃‍♂️':     1.75,
        'VERY ACTIVE 🏋️': 1.975
    }
    return rmr * activity.get(activity_level, 1.2)

def calc_macros(W, target_cal, activity_level, prog):
    """
    Fats:    Fixed per activity level, goal-independent
             Scales with activity to support hormonal and joint health
    Protein: Goal-aware, increases with activity — Cut > Maintain > Bulk
    Carbs:   Pure remainder — always hits target_cal exactly

    Calorie values: Protein = 4 kcal/g, Fat = 9 kcal/g, Carbs = 4 kcal/g
    W in kg, target_cal in kcal.
    """

    fats_per_kg = {
        'SEDENTARY 🛌':   1.0,
        'LIGHT 🧘‍♂️':      1.0,
        'MODERATE 🧖‍♂️':   1.0,
        'ACTIVE 🏃‍♂️':     1.1,
        'VERY ACTIVE 🏋️': 1.15
    }

    protein_bulk = {
        'SEDENTARY 🛌':   0.8,
        'LIGHT 🧘‍♂️':      0.8,
        'MODERATE 🧖‍♂️':   1.2,
        'ACTIVE 🏃‍♂️':     1.75,
        'VERY ACTIVE 🏋️': 2.1
    }

    protein_maintain = {
        'SEDENTARY 🛌':   0.8,
        'LIGHT 🧘‍♂️':      0.95,
        'MODERATE 🧖‍♂️':   1.25,
        'ACTIVE 🏃‍♂️':     1.95,
        'VERY ACTIVE 🏋️': 2.15
    }

    protein_cut = {
        'SEDENTARY 🛌':   1.0,
        'LIGHT 🧘‍♂️':      1.2,
        'MODERATE 🧖‍♂️':   1.5,
        'ACTIVE 🏃‍♂️':     2.1,
        'VERY ACTIVE 🏋️': 2.3
    }

    if "LOSE" in prog:
        protein_table = protein_cut
    elif "GAIN" in prog:
        protein_table = protein_bulk
    else:  # MAINTAIN
        protein_table = protein_maintain

    fats_g    = round(W * fats_per_kg.get(activity_level, 1.0))
    protein_g = round(W * protein_table.get(activity_level, 1.6))
    carbs_g   = round(max(target_cal - (protein_g * 4) - (fats_g * 9), 0) / 4)

    return protein_g, fats_g, carbs_g

def calc_fiber(target_cal):
    """
    Fiber — IOM standard: 14g per 1000 kcal.
    Applies equally to males and females.
    Women naturally get lower targets due to lower calorie intake.
    """
    return round((target_cal / 1000) * 14)

def calc_micros(S, A, activity_level):
    """
    Micronutrient targets based on:
    - ICMR-NIN 2020 RDA as base values (sex and age dependent)
    - Activity-level bumps for micros with strong evidence of
      increased need in athletes (sweat loss, energy metabolism,
      oxidative stress, bone remodeling)

    Returns a dict of {nutrient: (value, unit)}
    """

    is_male = S.lower() == "m"

    # --- BASE RDA (ICMR-NIN 2020) ---
    vit_a    = 900   if is_male else 700
    vit_d    = 600
    vit_c    = 80    if is_male else 65
    vit_e    = 15
    vit_k    = 120   if is_male else 90
    vit_b1   = 1.2   if is_male else 1.1
    vit_b2   = 1.3   if is_male else 1.1
    vit_b3   = 16    if is_male else 12
    vit_b6   = 1.3
    vit_b12  = 2.4
    folate   = 300   if is_male else 220
    calcium   = 1000
    phosphorus= 1000
    magnesium = 440  if is_male else 370
    iron      = 17   if is_male else 21
    zinc      = 17   if is_male else 13
    iodine    = 150
    selenium  = 40
    copper    = 2
    chromium  = 50
    manganese = 4
    potassium = 3500
    sodium    = 2000

    # --- ACTIVITY MULTIPLIERS ---
    activity_bumps = {
        'SEDENTARY 🛌':   {'vit_c': 1.0,  'vit_d': 1.0,  'iron': 1.0,  'magnesium': 1.0,  'zinc': 1.0,  'vit_b1': 1.0,  'vit_b2': 1.0,  'vit_b3': 1.0,  'vit_b6': 1.0,  'potassium': 1.0,  'sodium': 1.0 },
        'LIGHT 🧘‍♂️':      {'vit_c': 1.25, 'vit_d': 1.0,  'iron': 1.0,  'magnesium': 1.0,  'zinc': 1.0,  'vit_b1': 1.1,  'vit_b2': 1.1,  'vit_b3': 1.1,  'vit_b6': 1.1,  'potassium': 1.0,  'sodium': 1.0 },
        'MODERATE 🧖‍♂️':   {'vit_c': 1.88, 'vit_d': 1.33, 'iron': 1.1,  'magnesium': 1.1,  'zinc': 1.1,  'vit_b1': 1.15, 'vit_b2': 1.15, 'vit_b3': 1.15, 'vit_b6': 1.15, 'potassium': 1.06, 'sodium': 1.15 },
        'ACTIVE 🏃‍♂️':     {'vit_c': 2.5,  'vit_d': 1.67, 'iron': 1.15, 'magnesium': 1.15, 'zinc': 1.15, 'vit_b1': 1.2,  'vit_b2': 1.2,  'vit_b3': 1.2,  'vit_b6': 1.2,  'potassium': 1.14, 'sodium': 1.25 },
        'VERY ACTIVE 🏋️': {'vit_c': 3.75, 'vit_d': 1.67, 'iron': 1.2,  'magnesium': 1.2,  'zinc': 1.2,  'vit_b1': 1.25, 'vit_b2': 1.25, 'vit_b3': 1.25, 'vit_b6': 1.25, 'potassium': 1.29, 'sodium': 1.5  },
    }

    b = activity_bumps.get(activity_level, activity_bumps['SEDENTARY 🛌'])

    return {
        "Vitamin A":              (round(vit_a),                       "µg"),
        "Vitamin D":              (round(vit_d * b['vit_d']),          "IU"),
        "Vitamin C":              (round(vit_c * b['vit_c']),          "mg"),
        "Vitamin E":              (round(vit_e),                       "mg"),
        "Vitamin K":              (round(vit_k),                       "µg"),
        "Vitamin B1 (Thiamine)":  (round(vit_b1 * b['vit_b1'], 1),    "mg"),
        "Vitamin B2 (Riboflavin)":(round(vit_b2 * b['vit_b2'], 1),    "mg"),
        "Vitamin B3 (Niacin)":    (round(vit_b3 * b['vit_b3']),       "mg"),
        "Vitamin B6":             (round(vit_b6 * b['vit_b6'], 1),    "mg"),
        "Vitamin B12":            (round(vit_b12, 1),                  "µg"),
        "Folate (B9)":            (round(folate),                      "µg"),
        "Calcium":                (round(calcium),                     "mg"),
        "Phosphorus":             (round(phosphorus),                  "mg"),
        "Magnesium":              (round(magnesium * b['magnesium']),  "mg"),
        "Iron":                   (round(iron * b['iron']),            "mg"),
        "Zinc":                   (round(zinc * b['zinc']),            "mg"),
        "Iodine":                 (round(iodine),                      "µg"),
        "Selenium":               (round(selenium),                    "µg"),
        "Copper":                 (round(copper, 1),                   "mg"),
        "Chromium":               (round(chromium),                    "µg"),
        "Manganese":              (round(manganese, 1),                "mg"),
        "Potassium":              (round(potassium * b['potassium']),  "mg"),
        "Sodium":                 (round(sodium * b['sodium']),        "mg"),
    }

def clean(text):
    """Strip non-ASCII characters for PDF compatibility."""
    text = text.replace("µg", "mcg")  # preserve µg before ASCII stripping
    return text.encode("ascii", "ignore").decode()

# --- PDF GENERATION ---

class FitnessReportPDF(FPDF):
    def __init__(self, name):
        super().__init__()
        self.report_name = name

    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(16, 185, 129)
        self.cell(0, 10, f"{clean(self.report_name)}'s Fitness Report", ln=True, align="C")

    def add_section(self, title, content):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(30, 41, 59)
        self.set_text_color(255)
        self.cell(0, 10, title, ln=True, fill=True)
        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        self.multi_cell(0, 10, clean(content))
        self.ln()

def generate_pdf(name, W, H, A, S, activity_level, prog, bmi, bmi_cat, bmr, rmr, mc, target_cal, protein, fats, carbs, fiber, micros):
    pdf = FitnessReportPDF(name)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_section("PERSONAL INFO",
        f"Name: {name}\nWeight: {W:.2f} kg\nHeight: {H:.2f} cm\nAge: {A} yrs\nSex: {S}\nActivity Level: {activity_level}\nGoal: {prog}")

    pdf.add_section("RESULTS",
        f"BMI: {bmi} ({bmi_cat})\nBMR: {round(bmr)} kcal/day\nRMR: {round(rmr)} kcal/day\nMaintenance Calories: {round(mc)} kcal/day\nTarget Calorie Intake: {round(target_cal)} kcal/day")

    pdf.add_section("TARGET MACROS",
        f"Protein: {protein} g\nFats: {fats} g\nCarbs: {carbs} g (of which Fiber: {fiber} g)")

    pdf.add_section("MACRO CALORIE BREAKDOWN",
        f"Protein: {protein} g x 4 = {protein * 4} kcal\nFats:    {fats} g x 9 = {fats * 9} kcal\nCarbs:   {carbs} g x 4 = {carbs * 4} kcal\nTotal:   {protein * 4 + fats * 9 + carbs * 4} kcal")

    vit_lines = "\n".join(
        f"{k}: {v} {u}"
        for k, (v, u) in micros.items()
        if any(x in k for x in ["Vitamin", "Folate"])
    )
    pdf.add_section("DAILY VITAMIN TARGETS", vit_lines)

    min_lines = "\n".join(
        f"{k}: {v} {u}"
        for k, (v, u) in micros.items()
        if not any(x in k for x in ["Vitamin", "Folate"])
    )
    pdf.add_section("DAILY MINERAL & ELECTROLYTE TARGETS", min_lines)

    pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="ignore")
    return BytesIO(pdf_bytes)