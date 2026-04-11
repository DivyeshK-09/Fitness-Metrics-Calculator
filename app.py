import streamlit as st
from main import (calc_bmi, get_bmi_category, calc_bmr, calc_rmr, calc_mc, calc_macros, calc_fiber, calc_micros, convert_weight, convert_height, generate_pdf)

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
    .micro-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #6366f1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
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
st.title("🏋️‍♂️ FITNESS METRICS CALCULATOR")

with st.form("input_form"):
    st.subheader("👤 Enter Personal Info")
    st.markdown("**Name**")
    name = st.text_input(" ", key="name_input", label_visibility="collapsed").strip().title()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Weight**")
        wc1, wc2 = st.columns([2.5, 1])
        with wc1:
            W_raw = st.number_input(" ", key="weight_input", label_visibility="collapsed")
        with wc2:
            weight_unit = st.selectbox(" ", ["kg", "lbs", "st", "oz"], index=0, key="weight_unit", label_visibility="collapsed")
        A = st.number_input("**Age (Years)**", min_value=1)

    with col2:
        st.markdown("**Height**")
        hc1, hc2 = st.columns([2.5, 1])
        with hc1:
            height_input = st.text_input(" ", placeholder="e.g.- 180/ 1.8/ 5'11", key="height_input", label_visibility="collapsed")
        with hc2:
            height_unit = st.selectbox(" ", ["cm", "m", "ft"], index=0, key="height_unit", label_visibility="collapsed")
        S = st.radio("**Sex**", ["M", "F"], horizontal=True)

    activity_level = st.selectbox("🏃‍♂️ **Activity Level**", [
        'SEDENTARY 🛌', 'LIGHTLY ACTIVE 🧘‍♂️', 'MODERATE 🧖‍♂️',
        'ACTIVE 🏃‍♂️', 'VERY ACTIVE 🏋️'
    ])
    with st.expander("🛈 Activity Info", expanded=False):
        st.markdown(tooltip_text, unsafe_allow_html=True)

    st.markdown("**Goal**")
    prog = st.radio(" ", ['GAIN MASS', 'MAINTAIN', 'LOSE FAT'], horizontal=True, label_visibility="collapsed")
    submitted = st.form_submit_button("🔍 CALCULATE")

if submitted and name:
    # Convert units → kg and cm
    W = convert_weight(W_raw, weight_unit)
    H, error = convert_height(height_input, height_unit)
    if error:
        st.error(error)
        st.stop()

    # Calculate
    bmi     = calc_bmi(W, H)
    bmi_cat = get_bmi_category(bmi)
    rmr     = calc_rmr(W, H, A, S)   # Mifflin-St Jeor — drives all calculations
    bmr     = calc_bmr(rmr)           # 90% of RMR — display only
    mc      = calc_mc(rmr, activity_level)  # TDEE from RMR

    if "GAIN" in prog:
        target_cal = mc + 500
    elif "LOSE" in prog:
        target_cal = mc - 500
    else:  # MAINTAIN
        target_cal = mc

    protein, fats, carbs = calc_macros(W, target_cal, activity_level, prog)
    fiber  = calc_fiber(target_cal)
    micros = calc_micros(S, A, activity_level)

    # --- RESULTS ---
    st.subheader("📊 Results")
    st.markdown(f"""
    <div class="result-card"><h3>📏 BMI:</h3><p>{bmi} — {bmi_cat}</p></div>
    <div class="result-card"><h3>🔥 BMR:</h3><p>{round(bmr)} kcal/day</p></div>
    <div class="result-card"><h3>🛌 RMR:</h3><p>{round(rmr)} kcal/day</p></div>
    <div class="result-card"><h3>⚡ MAINTENANCE CALORIES:</h3><p>{round(mc)} kcal/day</p></div>
    <div class="result-card"><h3>🎯 TARGET CALORIE INTAKE ({prog}):</h3><p>{round(target_cal)} kcal/day</p></div>
    """, unsafe_allow_html=True)

    # --- MACROS ---
    with st.expander("🍱 TARGET MACRONUTRIENTS PER DAY"):
        st.markdown(f"""
        <div class="result-card">
            <strong>Protein:</strong> {protein} g ({protein * 4} kcal)<br>
            <strong>Fats:</strong> {fats} g ({fats * 9} kcal)<br>
            <strong>Carbohydrates:</strong> {carbs} g ({carbs * 4} kcal)<br>
            <span style="margin-left: 1.5rem; color: #94a3b8;">
                └─ of which Fiber: {fiber} g
            </span><br><br>
            <strong>Total Macro Calories:</strong> {protein * 4 + fats * 9 + carbs * 4} kcal
        </div>
        """, unsafe_allow_html=True)

    # --- MICROS ---
    with st.expander("🔬 DAILY MICRONUTRIENT TARGETS"):
        vitamins = {k: v for k, v in micros.items() if any(x in k for x in ["Vitamin", "Folate"])}
        minerals = {k: v for k, v in micros.items() if not any(x in k for x in ["Vitamin", "Folate"])}

        st.markdown("##### 💊 Vitamins")
        vit_rows = "".join(
            f"<tr><td style='padding: 6px 12px; color:#94a3b8;'>{k}</td>"
            f"<td style='padding: 6px 12px; font-weight:bold;'>{v} {u}</td></tr>"
            for k, (v, u) in vitamins.items()
        )
        st.markdown(f"""
        <div class="micro-card">
            <table style='width:100%; border-collapse: collapse;'>
                {vit_rows}
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🪨 Minerals & Electrolytes")
        min_rows = "".join(
            f"<tr><td style='padding: 6px 12px; color:#94a3b8;'>{k}</td>"
            f"<td style='padding: 6px 12px; font-weight:bold;'>{v} {u}</td></tr>"
            for k, (v, u) in minerals.items()
        )
        st.markdown(f"""
        <div class="micro-card">
            <table style='width:100%; border-collapse: collapse;'>
                {min_rows}
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='color:#64748b; font-size:0.8em;'>⚠️ These are daily targets. "
            "Micros bumped from base RDA for Iron, Magnesium, Zinc, B-Vitamins, Vitamin C, D, "
            "Potassium and Sodium based on activity level. Meet these through whole foods first — "
            "supplement only for diagnosed deficiencies.</p>",
            unsafe_allow_html=True
        )

    # --- PDF ---
    pdf_output = generate_pdf(
        name, W, H, A, S, activity_level, prog,
        bmi, bmi_cat, bmr, rmr, mc, target_cal,
        protein, fats, carbs, fiber, micros
    )

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_output,
        file_name=f"{name.replace(' ', '_').lower()}_fitness_report.pdf",
        mime="application/pdf"
    )