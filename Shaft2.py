# FatigPro - Streamlit App for Shaft Fatigue Evaluation
import streamlit as st
import pandas as pd
import math

# Configure page
st.set_page_config(layout="wide", page_title="FatigPro - Shaft Fatigue Evaluation")

# Main header
st.header("FatigPro - Shaft Fatigue Failure Evaluation")

# Display figures in tabs
fig1, fig2, fig3 = st.tabs(["Shaft Diagram", "Notch Sensitivity", "Stress Concentration"])

with fig1:
    st.image("https://media.cheggcdn.com/media/ceb/ceb70f1b-5eef-456b-b792-2370380aa91c/phpXXeZ27",
             caption="Fig. 1: Shaft Diagram", width=600)

with fig2:
    st.image("https://www.researchgate.net/publication/44220429/figure/download/fig1/AS:670016391356455@1536755764941/Notch-sensitivity-versus-notch-radius-for-steels-and-aluminium-alloys.png",
             caption="Fig. 2: Notch Sensitivity Chart", width=600)

with fig3:
    st.image("https://www.engineersedge.com/materials/images/stress-concentration-2.png",
             caption="Fig. 3: Stress Concentration Factors", width=600)

# Sidebar input
st.sidebar.header('Input Parameters')

def user_input_features():
    with st.sidebar.expander("Dimensional Parameters"):
        Da = st.number_input('Major Diameter (Da, mm)', min_value=0.1, value=10.0)
        Db = st.number_input('Minor Diameter (Db, mm)', min_value=0.1, value=8.0)
        r = st.number_input('Notch radius (r, mm)', min_value=0.1, value=1.0)
        
    with st.sidebar.expander("Loading Conditions"):
        F = st.number_input('Applied Force (F, N)', min_value=0.0, value=100.0)
        mean_torque = st.number_input('Mean Torque (Tmean, N·mm)', min_value=0.0, value=5000.0)
        alternating_torque = st.number_input('Alternating Torque (Talt, N·mm)', min_value=0.0, value=2000.0)
        
    with st.sidebar.expander("Material Properties"):
        UTS = st.number_input('Ultimate Tensile Strength (UTS, MPa)', min_value=0.1, value=690.0)
        Sy = st.number_input('Yield Strength (Sy, MPa)', min_value=0.1, value=550.0)
        f = st.number_input('Fatigue Strength Fraction (f)', min_value=0.0, max_value=1.0, value=0.85)
    
    # Calculate Kt based on geometry
    Dd_ratio = Da / Db
    rd_ratio = r / Db
    Kt = 1.0 + 0.5 * (Dd_ratio - 1) * (1 + 1 / math.sqrt(rd_ratio))
    
    return {
        'Da': Da, 'Db': Db, 'r': r,
        'F': F, 'mean_torque': mean_torque, 'alt_torque': alternating_torque,
        'UTS': UTS, 'Sy': Sy, 'f': f, 'Kt': Kt
    }

def perform_calculations(inputs):
    results = {}
    
    # Fatigue strength calculations
    Se_prime = 0.5 * inputs['UTS']
    results['Se_prime'] = Se_prime
    
    # Notch sensitivity and Kf
    if 340 <= inputs['UTS'] <= 1700:
        NC = 1.24 - 2.25e-3 * inputs['UTS'] + 1.60e-6 * inputs['UTS']**2 - 4.11e-10 * inputs['UTS']**3
        Kf = 1 + (inputs['Kt'] - 1)/(1 + NC/math.sqrt(inputs['r']))
    else:
        NC = None
        Kf = None
    
    # Stress calculations
    M_B = inputs['F'] * inputs['Db'] / 2  # Simple bending moment approximation
    Z = (math.pi * inputs['Db']**3) / 32
    sigma_a = (M_B / Z) * Kf if Kf else None
    
    # Combined stresses
    tau_m = 16 * inputs['mean_torque'] / (math.pi * inputs['Db']**3)
    tau_a = 16 * inputs['alt_torque'] / (math.pi * inputs['Db']**3)
    
    sigma_a_prime = math.sqrt(sigma_a**2 + 3 * tau_a**2) if sigma_a else None
    sigma_m_prime = math.sqrt(0 + 3 * tau_m**2)  # Assuming sigma_m = 0
    
    # Finite life calculations
    if sigma_a_prime and Se_prime and inputs['f']:
        a = (inputs['f'] * inputs['UTS'])**2 / Se_prime
        b = -(1/3) * math.log10((inputs['f'] * inputs['UTS']) / Se_prime)
        N = (sigma_a_prime / a)**(1/b) if (a > 0 and b != 0) else None
        
        results.update({
            'Finite Life a': a,
            'Finite Life b': b,
            'Cycles to Failure N': N
        })
    
    return results

# Main app
inputs = user_input_features()
results = perform_calculations(inputs)

# Display Results
st.subheader("Finite Life Results")
if 'Cycles to Failure N' in results and results['Cycles to Failure N']:
    st.table(pd.DataFrame({
        'Parameter': ['a', 'b', 'Cycles to Failure (N)'],
        'Value': [
            f"{results['Finite Life a']:.1f}",
            f"{results['Finite Life b']:.4f}",
            f"{results['Cycles to Failure N']/1000:.1f} × 10³"
        ],
        'Units': ['MPa', '-', 'cycles']
    }))
else:
    st.warning("Finite life calculations not applicable - check input conditions")
