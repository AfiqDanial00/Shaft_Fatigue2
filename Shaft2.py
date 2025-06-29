# FatigPro - Updated Streamlit App for Shaft Fatigue Evaluation
import streamlit as st
import pandas as pd
import math
import numpy as np

# Configure page
st.set_page_config(layout="wide", page_title="FatigPro-Advanced Shaft Fatigue Failure Evaluation")

# Main header
st.header("FatigPro-Advanced Shaft Fatigue Failure Evaluation")

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
        f = st.number_input('Fatigue Strength Fraction (f)', min_value=0.0, max_value=1.0, value=0.85)

    with st.sidebar.expander("Loading Conditions"):
        F = st.number_input('Applied Force (F,N)', min_value=0.0, value=100.0)
        mean_torque = st.number_input('Mean Torque (Tmean, N·mm)', min_value=0.0, value=5000.0)
        alternating_torque = st.number_input('Alternating Torque (Talt, N·mm)', min_value=0.0, value=2000.0)

    with st.sidebar.expander("Material Properties"):
        UTS = st.number_input('Ultimate Tensile Strength (UTS, MPa)', min_value=0.1, value=690.0)
        Sy = st.number_input('Yield Strength (Sy, MPa)', min_value=0.1, value=550.0)
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

[Rest of your code remains the same...]
