import streamlit as st
from fpdf import FPDF
from io import BytesIO
import re

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #10b981;
    }
    .stRadio label, .stSelectbox label, .stNumberInput label {
        font-weight: bold;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 0.2rem !important;
    }
    .stSelectbox > div {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    .result-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #10b981;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        color: #f1f5f9;
    }
    .stButton button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #059669;
    }
    .stRadio > div {
        flex-direction: row;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def calc_bmi(W, H):
    return round((W / (H / 100) ** 2), 1)

def calc_bmr(W, H, A, S):
    return 66.47 + (13.75 * W) + (5.0033 * H) - (6.75 * A) if S.lower() == "m" else 447.59 + (9.24 * W) + (3.09 * H) - (4.33 * A)

def calc_rmr(W, H, A, S):
    return 260 + (9.65 * W) + (5.73 * H) - (5.08 * A) if S.lower() == "m" else 43 + (7.38 * W) + (6.07 * H) - (2.31 * A)

def calc_mc(bmr, activity_level):
    activity = {
        'SEDENTARY 🛌': 1.2,
        'LIGHT 🧘‍♂️': 1.375,
        'MODERATE 🧖‍♂️': 1.55,
        'ACTIVE 🏃‍♂️': 1.725,
        'VERY ACTIVE 🏋️': 1.9
    }
    return bmr * activity.get(activity_level, 1.2)

def calc_macros(W, activity_level):
    pm = {'SEDENTARY 🛌': 0.8, 'LIGHT 🧘‍♂️': 0.8, 'MODERATE 🧖‍♂️': 1.2, 'ACTIVE 🏃‍♂️': 1.7, 'VERY ACTIVE 🏋️': 2}
    fm = {'SEDENTARY 🛌': 0.35, 'LIGHT 🧘‍♂️': 0.35, 'MODERATE 🧖‍♂️': 0.55, 'ACTIVE 🏃‍♂️': 0.8, 'VERY ACTIVE 🏋️': 1.0}
    cm = {'SEDENTARY 🛌': 3.5, 'LIGHT 🧘‍♂️': 3.5, 'MODERATE 🧖‍♂️': 4.25, 'ACTIVE 🏃‍♂️': 4.85, 'VERY ACTIVE 🏋️': 5.5}
    return round(W * pm.get(activity_level, 0.8)), round(W * fm.get(activity_level, 0.3)), round(W * cm.get(activity_level, 3.5))

def clean(text):
    return text.encode("ascii", "ignore").decode()

tooltip_text = """
<table style='width:100%; font-size: 0.85em;'>
  <tr>
    <td style='color:#10b981; font-weight:bold;'>SEDENTARY</td>
    <td>Very little or no intentional exercise (Basically just lying around, watching TV and basic household chores).</td>
  </tr>
  <tr>
    <td style='color:#10b981; font-weight:bold;'>LIGHTLY ACTIVE</td>
    <td>Light physical activities like yoga, basic stretchings, brisk walking 4-5 kmph (45-60 mins).</td>
  </tr>
  <tr>
    <td style='color:#10b981; font-weight:bold;'>MODERATE</td>
    <td>Activities like casual sports, body weight workout, light weight training, jogging at 8-9 kmph (60-90 mins).</td>
  </tr>
  <tr>
    <td style='color:#10b981; font-weight:bold;'>ACTIVE</td>
    <td>Intense training like weight training, calisthenics, competitive sports (120-150 mins; 3-5 days a week).</td>
  </tr>
  <tr>
    <td style='color:#10b981; font-weight:bold;'>VERY ACTIVE</td>
    <td>Very intense weight training, intense sports, extremely volumetric workout (150+ mins, 6-7 days a week).</td>
  </tr>
</table>
"""

# --- UI ---
st.title("🏋️‍♂️ Fitness Metrics Calculator")

with st.form("input_form"):
    st.subheader("👤 Enter Personal Info")
    name = st.text_input("Name").strip().title()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Weight**")
        wc1, wc2 = st.columns([4, 1])
        with wc1:
            W_raw = st.number_input(" ", min_value=1.0, key="weight_input", label_visibility="collapsed")
        with wc2:
            weight_unit = st.selectbox(" ", ["kg", "lbs", "st", "oz"], index=0, key="weight_unit", label_visibility="collapsed")
        A = st.number_input("Age (Years)", min_value=1)

    with col2:
        st.markdown("**Height**")
        hc1, hc2 = st.columns([4, 1])
        with hc1:
            height_input = st.text_input(" ", placeholder="e.g. 180 or 5'11.5\"", key="height_input", label_visibility="collapsed")
        with hc2:
            height_unit = st.selectbox(" ", ["cm", "m", "ft"], index=0, key="height_unit", label_visibility="collapsed")
        S = st.radio("Sex", ["M", "F"], horizontal=True)

    st.markdown("#### 🏃‍♂️ Activity Level")
    activity_level = st.selectbox("", [
        'SEDENTARY 🛌', 'LIGHT 🧘‍♂️', 'MODERATE 🧖‍♂️',
        'ACTIVE 🏃‍♂️', 'VERY ACTIVE 🏋️'
    ])
    with st.expander("🛈 Activity Info", expanded=False):
        st.markdown(tooltip_text, unsafe_allow_html=True)
    prog = st.radio("Goal", ['GAIN MASS', 'LOSE FAT'], horizontal=True)
    submitted = st.form_submit_button("🔍 CALCULATE")

if submitted and name:
    W = W_raw * 0.453592 if weight_unit == "pounds" else W_raw * 6.35029 if weight_unit == "stones" else W_raw * 0.0283495 if weight_unit == "ounces" else W_raw

    try:
        if height_unit == "feet+inches":
            match = re.match(r"^\s*(\d+)'(\d*\.?\d*)\s*\"?\s*$", height_input)
            if match:
                ft = float(match.group(1))
                inch = float(match.group(2))
                H = ft * 30.48 + inch * 2.54
            else:
                st.error("❌ Enter height like 5'11 or 6'0.5\"")
                H = 0
        elif height_unit == "meters":
            H = float(height_input) * 100
        else:
            H = float(height_input)
    except:
        st.error("❌ Invalid height input")
        H = 0

    bmi = calc_bmi(W, H)
    bmr = calc_bmr(W, H, A, S)
    rmr = calc_rmr(W, H, A, S)
    mc = calc_mc(bmr, activity_level)
    target_cal = mc + 500 if "GAIN" in prog else mc - 500
    protein, fats, carbs = calc_macros(W, activity_level)

    st.subheader("📊 Results")
    st.markdown(f"""
    <div class="result-card"><h3>📏 BMI:</h3><p>{bmi}</p></div>
    <div class="result-card"><h3>🔥 BMR:</h3><p>{round(bmr)} kcal/day</p></div>
    <div class="result-card"><h3>🛌 RMR:</h3><p>{round(rmr)} kcal/day</p></div>
    <div class="result-card"><h3>⚡ MAINTENANCE CALORIES:</h3><p>{round(mc)} kcal/day</p></div>
    <div class="result-card"><h3>🎯 TARGET CALORIE INTAKE ({prog}):</h3><p>{round(target_cal)} kcal/day</p></div>
    """, unsafe_allow_html=True)

    with st.expander("🍱 TARGET MACRONUTRIENTS PER DAY"):
        st.markdown(f"""
        <div class="result-card">
            <strong>Protein:</strong> {protein} g<br>
            <strong>Fats:</strong> {fats} g<br>
            <strong>Carbohydrates:</strong> {carbs} g
        </div>
        """, unsafe_allow_html=True)

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.set_text_color(16, 185, 129)
            self.cell(0, 10, f"{clean(name)}'s Fitness Report", ln=True, align="C")

        def add_section(self, title, content):
            self.set_font("Arial", "B", 12)
            self.set_fill_color(30, 41, 59)
            self.set_text_color(255)
            self.cell(0, 10, title, ln=True, fill=True)
            self.set_font("Arial", "", 11)
            self.set_text_color(0)
            self.multi_cell(0, 10, clean(content))
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_section("Personal Info", f"Name: {name}\nWeight: {W:.2f} kg\nHeight: {H:.2f} cm\nAge: {A} yrs\nSex: {S}\nActivity Level: {activity_level}\nGoal: {prog}")
    pdf.add_section("Results", f"BMI: {bmi}\nBMR: {round(bmr)} kcal/day\nRMR: {round(rmr)} kcal/day\nMaintenance Calories: {round(mc)} kcal/day\nTarget Calorie Intake: {round(target_cal)} kcal/day")
    pdf.add_section("Target Macros", f"Protein: {protein} g\nFats: {fats} g\nCarbs: {carbs} g")

    pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="ignore")
    pdf_output = BytesIO(pdf_bytes)

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_output,
        file_name=f"{name.replace(' ', '_').lower()}_fitness_report.pdf",
        mime="application/pdf"
    )
