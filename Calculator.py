import streamlit as st

# Styling
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
    .info-tooltip {
        display: inline-block;
        position: relative;
        cursor: help;
        font-size: 1em;
        width: 1.5em;
        height: 1.5em;
        background: #f1f5f9;
        color: #0f172a;
        border-radius: 50%;
        text-align: center;
        line-height: 1.5em;
        font-weight: bold;
        margin-top: 2.3em;
    }
    .info-tooltip {
        display: inline-block;
        position: relative;
        cursor: help;
        font-size: 1em;
        width: 1.5em;
        height: 1.5em;
        background: #f1f5f9;
        color: #0f172a;
        border-radius: 50%;
        text-align: center;
        line-height: 1.5em;
        font-weight: bold;
        margin-top: 2.3em;
        z-index: 5;
    }

    .custom-tooltip {
        display: none;
        position: absolute;
        left: -220px;
        top: 35px;
        width: 340px;
        background: #1e293b;
        color: #f1f5f9;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #10b981;
        font-size: 0.8em;
        z-index: 100;
        pointer-events: none;
    }

    .info-tooltip:hover + .custom-tooltip {
        display: block;
    }
    .stTooltip {
        z-index: 9999 !important;
        overflow: visible !important;
        white-space: normal !important;
        max-width: 400px !important;
    }
    .st-emotion-cache-1y4p8pa {
        overflow: visible !important;
    }
    </style>
""", unsafe_allow_html=True)

# Functions
def calc_bmi(W, H):
    return round((W / (H / 100) ** 2), 1)

def calc_bmr(W, H, A, S):
    return 66.47 + (13.75 * W) + (5.0033 * H) - (6.75 * A) if S.lower() == "m" else 447.59 + (9.24 * W) + (3.09 * H) - (4.33 * A)

def calc_rmr(W, H, A, S):
    return 260 + (9.65 * W) + (5.73 * H) - (5.08 * A) if S.lower() == "m" else 43 + (7.38 * W) + (6.07 * H) - (2.31 * A)

def calc_mc(bmr, activity_level):
    activity = {
        'SEDENTARY 🏋️': 1.2,
        'LIGHT 🧘‍♂️': 1.375,
        'MODERATE 🧖‍♂️': 1.55,
        'ACTIVE 🏃‍♂️': 1.725,
        'VERY ACTIVE 🏋️': 1.9
    }
    return bmr * activity.get(activity_level, 1.2)

def calc_macros(W, activity_level):
    protein_multipliers = {
        'SEDENTARY 🏋️': 0.8,
        'LIGHT 🧘‍♂️': 0.8,
        'MODERATE 🧖‍♂️': 1.2,
        'ACTIVE 🏃‍♂️': 1.7,
        'VERY ACTIVE 🏋️': 2
    }
    fat_multipliers = {
        'SEDENTARY 🏋️': 0.35,
        'LIGHT 🧘‍♂️': 0.35,
        'MODERATE 🧖‍♂️': 0.55,
        'ACTIVE 🏃‍♂️': 0.8,
        'VERY ACTIVE 🏋️': 1.0
    }
    carb_multipliers = {
        'SEDENTARY 🏋️': 3.5,
        'LIGHT 🧘‍♂️': 3.5,
        'MODERATE 🧖‍♂️': 4.25,
        'ACTIVE 🏃‍♂️': 4.85,
        'VERY ACTIVE 🏋️': 5.5
    }
    P = round(W * protein_multipliers.get(activity_level, 0.8))
    F = round(W * fat_multipliers.get(activity_level, 0.3))
    C = round(W * carb_multipliers.get(activity_level, 3.5))
    return P, F, C

# Hover-Icon's Contents
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

# UI
st.title("Fitness Metrics Calculator")

with st.form("input_form"):
    st.subheader("👤 Enter Information:")
    col1, col2 = st.columns(2)
    with col1:
        W = st.number_input("Weight (KG)", min_value=1.0)
        A = st.number_input("Age (Years)", min_value=1)
    with col2:
        H = st.number_input("Height (CM)", min_value=1.0)
        S = st.radio("Sex", ["M", "F"], horizontal=True, format_func=lambda x: x.upper())

    col1, col2 = st.columns([6, 1])
    with col1:
        activity_level = st.selectbox("Activity Level", [
            'SEDENTARY 🛌', 'LIGHT 🧘‍♂️', 'MODERATE 🧖‍♂️', 'ACTIVE 🏃‍♂️', 'VERY ACTIVE 🏋️'])
    with col2:
        st.markdown(f"""
        <div class="tooltip-container">
            <span class="info-tooltip">?</span>
            <div class="custom-tooltip">{tooltip_text}</div>
        </div>
    """, unsafe_allow_html=True)

    prog = st.radio("Goal", ['GAIN MASS', 'LOSE FAT'], horizontal=True)
    submitted = st.form_submit_button("🔍 CALCULATE")

# Metrics
if submitted:
    bmi = calc_bmi(W, H)
    bmr = calc_bmr(W, H, A, S)
    rmr = calc_rmr(W, H, A, S)
    mc = calc_mc(bmr, activity_level)
    suggested_cal = mc + 500 if "GAIN" in prog else mc - 500
    protein, fats, carbs = calc_macros(W, activity_level)

    st.subheader("📊 Results")
    st.markdown(f"""
    <div class="result-card"><h3>📏 BMI:</h3><p>{bmi}</p></div>
    <div class="result-card"><h3>🔥 BMR:</h3><p>{round(bmr)} kcal/day</p></div>
    <div class="result-card"><h3>🛌 RMR:</h3><p>{round(rmr)} kcal/day</p></div>
    <div class="result-card"><h3>⚡ MAINTENANCE CALORIES:</h3><p>{round(mc)} kcal/day</p></div>
    <div class="result-card"><h3>🎯 TARGET CALORIE INTAKE ({prog}):</h3><p>{round(suggested_cal)} kcal/day</p></div>
    """, unsafe_allow_html=True)

    with st.expander("🍱 MACRONUTRIENTS (Based on Activity)"):
        st.markdown(f"""
        <div class="result-card">
            <strong>PROTEIN:</strong> {protein} g  
            <br><strong>FATS:</strong> {fats} g  
            <br><strong>CARBOHYDRATES:</strong> {carbs} g
        </div>
        """, unsafe_allow_html=True)
        
    st.success("✅ All values calculated! Adjust your diet accordingly.")

# Credits
st.markdown("""
---
<div style='text-align: center; padding-top: 20px;'>
    <p style='color:#94a3b8;'>Developed by <strong>Divyesh Kulshreshtha</strong></p>
    <a href='https://github.com/DivyeshK-09' target='_blank' style='margin-right:15px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/733/733553.png' width='30' style='vertical-align: middle;' title='GitHub Profile'/>
    </a>
    <a href='mailto:divyesh.kulshreshtha.09@gmail.com'>
        <img src='https://cdn-icons-png.flaticon.com/512/732/732200.png' width='30' style='vertical-align: middle;' title='Email'/>
    </a>
</div>
""", unsafe_allow_html=True)
