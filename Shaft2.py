import streamlit as st
import pandas as pd
import math
import numpy as np

# Configure page
st.set_page_config(layout="wide", page_title="Advanced Shaft Fatigue Evaluation")

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

# Input parameters in sidebar
st.sidebar.header('User Input Parameters')

def user_input_features():
    with st.sidebar.expander("Dimensional Parameters"):
        Da = st.number_input('Major Diameter (Da, mm)', min_value=0.1, value=10.0, step=0.1, format="%.3f")
        Db = st.number_input('Minor Diameter (Db, mm)', min_value=0.1, value=8.0, step=0.1, format="%.3f")
        L = st.number_input('Shaft Length (L, mm)', min_value=0.1, value=100.0, step=0.1, format="%.3f")
        r = st.number_input('Notch radius (r, mm)', min_value=0.1, value=1.0, step=0.1, format="%.3f",
                          help="Refer to Figure 1 for location")
        Lfa = st.number_input('Distance Fa to end (Lfa, mm)', min_value=0.0, value=20.0, step=0.1, format="%.3f")
        Lfb = st.number_input('Distance Fb to end (Lfb, mm)', min_value=0.0, value=30.0, step=0.1, format="%.3f")
    
    with st.sidebar.expander("Loading Conditions"):
        F = st.number_input('Applied Force (F,N)', min_value=0.0, value=100.0, step=1.0, format="%.3f")
        mean_torque = st.number_input('Mean Torque (Tmean, N·mm)', min_value=0.0, value=5000.0, step=100.0, format="%.3f")
        alternating_torque = st.number_input('Alternating Torque (Talt, N·mm)', min_value=0.0, value=2000.0, step=100.0, format="%.3f")
    
    with st.sidebar.expander("Material Properties"):
        UTS = st.number_input('Ultimate Tensile Strength (UTS, MPa)', min_value=0.1, value=500.0, step=10.0, format="%.3f")
        Sy = st.number_input('Yield Strength (Sy, MPa)', min_value=0.1, value=300.0, step=10.0, format="%.3f")
        a = st.number_input('Surface factor constant (a)', min_value=0.001, value=1.34, step=0.01, format="%.3f")
        b = st.number_input('Surface factor exponent (b)', min_value=-1.0, value=-0.085, step=0.001, format="%.3f")
    
    # Calculate geometric ratios for Kt
    Dd_ratio = Da / Db
    rd_ratio = r / Db
    
    # Kt estimation (simplified - should be replaced with proper interpolation)
    Kt = 1.0 + 0.5*(Dd_ratio-1)*(1 + 1/math.sqrt(rd_ratio))
    
    data = {
        'Da (mm)': Da, 'Db (mm)': Db, 'L (mm)': L, 'r (mm)': r,
        'F (N)': F, 'Lfa (mm)': Lfa, 'Lfb (mm)': Lfb,
        'UTS (MPa)': UTS, 'Sy (MPa)': Sy, 'a': a, 'b': b, 'Kt': Kt,
        'Tmean (N·mm)': mean_torque, 'Talt (N·mm)': alternating_torque
    }
    
    return pd.DataFrame(data, index=[0])

# Calculations following Shigley's methodology
def perform_calculations(df):
    # Extract values
    Da = df['Da (mm)'].values[0]
    Db = df['Db (mm)'].values[0]
    L = df['L (mm)'].values[0]
    r = df['r (mm)'].values[0]
    F = df['F (N)'].values[0]
    Lfa = df['Lfa (mm)'].values[0]
    Lfb = df['Lfb (mm)'].values[0]
    UTS = df['UTS (MPa)'].values[0]
    Sy = df['Sy (MPa)'].values[0]
    a = df['a'].values[0]
    b = df['b'].values[0]
    Kt = df['Kt'].values[0]
    Tmean = df['Tmean (N·mm)'].values[0]
    Talt = df['Talt (N·mm)'].values[0]
    
    # Core calculations
    results = {}
    
    # 1. Fatigue strength calculations 
    results['Se_prime (MPa)'] = 0.5 * UTS  # Eq. 6-8
    
    # Surface factor (ka)
    results['ka'] = a * (UTS ** b)  # Eq. 6-19
    
    # Size factor (kb)
    if 2.79 <= Db <= 51:  # Eq. 6-20
        results['kb'] = 1.24 * (Db ** -0.107)
    elif 51 < Db <= 254:
        results['kb'] = 1.51 * (Db ** -0.157)
    else:
        results['kb'] = None
    
    # Corrected endurance limit
    if results['kb'] is not None:
        results['Se (MPa)'] = results['ka'] * results['kb'] * results['Se_prime (MPa)']  # Eq. 6-18
    else:
        results['Se (MPa)'] = None
    
    # 2. Neuber's constant (for bending/axial)
    if 340 <= UTS <= 1700:  # Eq. 6-35a
        results['NC (√mm)'] = 1.24 - 2.25e-3*UTS + 1.60e-6*(UTS**2) - 4.11e-10*(UTS**3)
    else:
        results['NC (√mm)'] = None
    
    # 3. Stress concentration factors
    results['Kt'] = Kt
    if 'NC (√mm)' in results and results['NC (√mm)'] is not None:
        results['Kf'] = 1 + (Kt - 1)/(1 + results['NC (√mm)']/math.sqrt(r))  # Eq. 6-33
    else:
        results['Kf'] = None
    
    # 4. Bending stresses
    results['M_B (N·m)'] = (((Lfa * F) / L) * 250)/1000 # Bending moment at critical location
    results['Section Modulus (mm³)'] = ((math.pi * Db**3) / 32)/(1000) # For circular cross-section
    
    if results['Kf'] is not None and results['Section Modulus (mm³)'] > 0:
        # Alternating bending stress (σa)
        results['σ_a (MPa)'] = (results['Kf'] * results['M_B (N·m)'] )/ (results['Section Modulus (mm³)'])
        
        # Mean bending stress (σm) - assuming R=0 loading (fully reversed)
        results['σ_m (MPa)'] = 0.0
        
        # Combined stresses (for torsion)
        results['τ_m (MPa)'] = 16 * Tmean / (math.pi * Db**3)  # Mean shear stress
        results['τ_a (MPa)'] = 16 * Talt / (math.pi * Db**3)   # Alternating shear stress
        
        # Maximum and minimum stresses (Eq. 6-36 to 6-38)
        results['σ_max (MPa)'] = results['σ_m (MPa)'] + results['σ_a (MPa)']
        results['σ_min (MPa)'] = results['σ_m (MPa)'] - results['σ_a (MPa)']
        
        # Von Mises equivalent stresses (Eq. 6-55, 6-56)
        σa_prime = math.sqrt(results['σ_a (MPa)']**2 + 3*results['τ_a (MPa)']**2)
        σm_prime = math.sqrt(results['σ_m (MPa)']**2 + 3*results['τ_m (MPa)']**2)
        
        results['σa_prime (MPa)'] = σa_prime
        results['σm_prime (MPa)'] = σm_prime
        
        # Safety factor using Modified Goodman (Eq. 6-46)
        if results['Se (MPa)'] is not None and UTS > 0:
            n = 1/(σa_prime/results['Se (MPa)'] + σm_prime/UTS)
            results['Safety Factor (n)'] = n
        else:
            results['Safety Factor (n)'] = None
    else:
        results['σ_a (MPa)'] = None
        results['σ_m (MPa)'] = None
        results['σ_max (MPa)'] = None
        results['σ_min (MPa)'] = None
        results['Safety Factor (n)'] = None
    
    return results

# Format numbers to 3 decimal places
def format_results(results):
    formatted = {}
    for key, value in results.items():
        if value is None:
            formatted[key] = "N/A"
        elif isinstance(value, str):
            formatted[key] = value
        else:
            formatted[key] = f"{float(value):.3f}"
    return formatted

# Main app flow
df = user_input_features()
results = perform_calculations(df)
formatted_results = format_results(results)

# Display results
st.subheader("Input Parameters")
st.dataframe(df.style.format("{:.3f}"), use_container_width=True)

st.subheader("Fatigue Strength Calculations")
fatigue_results = {
    'Parameter': ['Endurance Limit (Se\')', 'Surface Factor (ka)', 
                 'Size Factor (kb)', 'Corrected Endurance Limit (Se)'],
    'Value': [
        formatted_results['Se_prime (MPa)'],
        formatted_results['ka'],
        formatted_results['kb'],
        formatted_results['Se (MPa)']
    ],
    'Units': ['MPa', '-', '-', 'MPa']
}
st.table(pd.DataFrame(fatigue_results))

st.subheader("Stress Analysis")
stress_results = {
    'Parameter': ['Theoretical Kt', 'Fatigue Kf', 
                 'Bending Moment', 'Section Modulus',
                 'Alternating Stress (σa)', 'Mean Stress (σm)',
                 'Max Stress (σmax)', 'Min Stress (σmin)',
                 'Alternating Von Mises (σa\')', 'Mean Von Mises (σm\')'],
    'Value': [
        formatted_results['Kt'],
        formatted_results['Kf'],
        formatted_results['M_B (N·m)'],
        formatted_results['Section Modulus (mm³)'],
        formatted_results['σ_a (MPa)'],
        formatted_results['σ_m (MPa)'],
        formatted_results['σ_max (MPa)'],
        formatted_results['σ_min (MPa)'],
        formatted_results['σa_prime (MPa)'],
        formatted_results['σm_prime (MPa)']
    ],
    'Units': ['-', '-', 'N·m', 'mm³', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa']
}
st.table(pd.DataFrame(stress_results))

# Safety factor display
if results['Safety Factor (n)'] is not None:
    st.metric("Safety Factor (Modified Goodman)", value=f"{results['Safety Factor (n)']:.3f}")
else:
    st.warning("Cannot calculate safety factor - missing required parameters")

# Add download button for results
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(df)
st.download_button(
    label="Download Input Parameters",
    data=csv,
    file_name='shaft_parameters.csv',
    mime='text/csv'
)
