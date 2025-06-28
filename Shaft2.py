# FatigPro - Updated Streamlit App for Shaft Fatigue Evaluation
import streamlit as st
import pandas as pd
import math
import numpy as np

# Configure page
st.set_page_config(layout="wide", page_title="FatigPro-Advanced Shaft Fatigue Failure Evaluation")

# Main header
st.header("Advanced Shaft Fatigue Evaluation System")

# Display figures in tabs
fig1, fig2, fig3 = st.tabs(["Shaft Diagram", "Notch Sensitivity", "Stress Concentration"])

with fig1:
    st.image("https://media.cheggcdn.com/media/ceb/ceb70f1b-5eef-456b-b792-2370380aa91c/phpXXeZ27",
             caption="Fig. 1: Schematic Drawing of Shaft with Dimensions", width=600)

with fig2:
    st.image("https://www.researchgate.net/publication/44220429/figure/download/fig1/AS:670016391356455@1536755764941/Notch-sensitivity-versus-notch-radius-for-steels-and-aluminium-alloys.png",
             caption="Fig. 2: Notch sensitivity versus notch radius", width=600)
    st.info("Use this chart to determine notch sensitivity (q) based on your material and notch radius")

with fig3:
    st.image("https://www.engineersedge.com/materials/images/stress-concentration-2.png",
             caption="Fig. 3: Stress concentration factor Kt vs r/d", width=600)
    st.info("Use this chart to determine Kt based on your shaft geometry")

# Sidebar input
st.sidebar.header('User Input Parameters')

def user_input_features():
    with st.sidebar.expander("Dimensional Parameters"):
        Da = st.number_input('Major Diameter (Da, mm)', min_value=0.1, value=10.0)
        Db = st.number_input('Minor Diameter (Db, mm)', min_value=0.1, value=8.0)
        L = st.number_input('Shaft Length (L, mm)', min_value=0.1, value=100.0)
        r = st.number_input('Notch radius (r, mm)', min_value=0.1, value=1.0)
        Lfa = st.number_input('Distance Fa to end (Lfa, mm)', min_value=0.0, value=20.0)
        Lfb = st.number_input('Distance Fb to end (Lfb, mm)', min_value=0.0, value=30.0)
        f = st.number_input('Fatigue Strength Fraction (f)', min_value=0.0, value=30.0)

    with st.sidebar.expander("Loading Conditions"):
        F = st.number_input('Applied Force (F,N)', min_value=0.0, value=100.0)
        mean_torque = st.number_input('Mean Torque (Tmean, N·mm)', min_value=0.0, value=5000.0)
        alternating_torque = st.number_input('Alternating Torque (Talt, N·mm)', min_value=0.0, value=2000.0)

    with st.sidebar.expander("Material Properties"):
        UTS = st.number_input('Ultimate Tensile Strength (UTS, MPa)', min_value=0.1, value=500.0)
        Sy = st.number_input('Yield Strength (Sy, MPa)', min_value=0.1, value=300.0)
        a_surf = st.number_input('Surface factor constant (a)', min_value=0.001, value=1.34)
        b_surf = st.number_input('Surface factor exponent (b)', min_value=-1.0, value=-0.085)

    Dd_ratio = Da / Db
    rd_ratio = r / Db
    Kt = 1.0 + 0.5 * (Dd_ratio - 1) * (1 + 1 / math.sqrt(rd_ratio))

    data = {
        'Da': Da, 'Db': Db, 'L': L, 'r': r, 'Lfa': Lfa, 'Lfb': Lfb,
        'F': F, 'f': f, 'UTS': UTS, 'Sy': Sy, 'a_surf': a_surf, 'b_surf': b_surf,
        'mean_torque': mean_torque, 'alt_torque': alternating_torque, 'Kt': Kt
    }

    return pd.DataFrame(data, index=[0])

def perform_calculations(df):
    vals = df.iloc[0]
    results = {}

    Se_prime = 0.5 * vals['UTS']
    ka = vals['a_surf'] * (vals['UTS'] ** vals['b_surf'])

    if 2.79 <= vals['Db'] <= 51:
        kb = 1.24 * (vals['Db'] ** -0.107)
    elif 51 < vals['Db'] <= 254:
        kb = 1.51 * (vals['Db'] ** -0.157)
    else:
        kb = None

    Se = ka * kb * Se_prime if kb is not None else None

    if 340 <= vals['UTS'] <= 1700:
        NC = 1.24 - 2.25e-3 * vals['UTS'] + 1.60e-6 * vals['UTS']**2 - 4.11e-10 * vals['UTS']**3
    else:
        NC = None

    Kf = 1 + (vals['Kt'] - 1)/(1 + NC/math.sqrt(vals['r'])) if NC else None

    M_B = (((vals['Lfa'] * vals['F']) / vals['L']) * 250)/1000
    Z = (math.pi * vals['Db']**3) / (32 * 1000)

    if Kf and Z > 0:
        sigma_a = (M_B / Z) * Kf
        sigma_m = 0.0
        tau_m = 16 * vals['mean_torque'] / (math.pi * vals['Db']**3)
        tau_a = 16 * vals['alt_torque'] / (math.pi * vals['Db']**3)

        sigma_max = sigma_m + sigma_a
        sigma_min = sigma_m - sigma_a

        sigma_a_prime = math.sqrt(sigma_a**2 + 3 * tau_a**2)
        sigma_m_prime = math.sqrt(sigma_m**2 + 3 * tau_m**2)

        n = 1 / (sigma_a_prime / Se + sigma_m_prime / vals['UTS']) if Se else None
    else:
        sigma_a = sigma_m = tau_m = tau_a = sigma_max = sigma_min = sigma_a_prime = sigma_m_prime = n = None

    results.update({
        'Se_prime': Se_prime, 'ka': ka, 'kb': kb, 'Se': Se,
        'NC': NC, 'Kt': vals['Kt'], 'Kf': Kf, 'M_B': M_B, 'Z': Z,
        'σ_a': sigma_a, 'σ_m': sigma_m, 'τ_m': tau_m, 'τ_a': tau_a,
        'σ_max': sigma_max, 'σ_min': sigma_min,
        'σa_prime': sigma_a_prime, 'σm_prime': sigma_m_prime,
        'Safety Factor': n
    })
    return results

def format_results(results):
    return {k: ("N/A" if v is None else f"{v:.3f}") for k, v in results.items()}

# Run App
input_df = user_input_features()
calc_results = perform_calculations(input_df)
formatted = format_results(calc_results)

# Display Results
st.subheader("Input Parameters")
st.dataframe(input_df.style.format("{:.3f}"), use_container_width=True)

st.subheader("Fatigue Strength Calculations")
st.table(pd.DataFrame({
    'Parameter': ["Se'", 'ka', 'kb', 'Se'],
    'Value': [formatted['Se_prime'], formatted['ka'], formatted['kb'], formatted['Se']],
    'Units': ['MPa', '-', '-', 'MPa']
}))

st.subheader("Stress Analysis")
st.table(pd.DataFrame({
    'Parameter': ['Kt', 'Kf', 'Bending Moment', 'Section Modulus', 'σa', 'σm', 'σmax', 'σmin', "σa'", "σm'"],
    'Value': [
        formatted['Kt'], formatted['Kf'], formatted['M_B'], formatted['Z'],
        formatted['σ_a'], formatted['σ_m'], formatted['σ_max'],
        formatted['σ_min'], formatted['σa_prime'], formatted['σm_prime']
    ],
    'Units': ['-', '-', 'N·m', 'mm³', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa']
}))

if calc_results['Safety Factor']:
    st.metric("Safety Factor (Modified Goodman)", f"{calc_results['Safety Factor']:.3f}")
else:
    st.warning("Unable to calculate Safety Factor. Check inputs.")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Input Parameters",
    convert_df(input_df),
    file_name="shaft_parameters.csv",
    mime="text/csv"
)  # End of script
