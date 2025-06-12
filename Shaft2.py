import streamlit as st
import pandas as pd
import math

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
        Da = st.number_input('Major Diameter (Da, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f")
        Db = st.number_input('Minor Diameter (Db, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f")
        L = st.number_input('Shaft Length (L, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f")
        r = st.number_input('Notch radius (r, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f",
                          help="Refer to Figure 1 for location")
        Lfa = st.number_input('Distance Fa to end (Lfa, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f")
        Lfb = st.number_input('Distance Fb to end (Lfb, mm)', min_value=0.01, value=0.01, step=0.01, format="%.3f")
    
    with st.sidebar.expander("Loading Conditions"):
        Fa = st.number_input('Force at A (Fa, N)', value=0.01, step=0.01, format="%.3f")
        Fb = st.number_input('Force at B (Fb, N)', value=0.01, step=0.01, format="%.3f")
        mean_load = st.number_input('Mean Load (N)', value=0.01, step=0.01, format="%.3f")
        amplitude_load = st.number_input('Amplitude Load (N)', value=0.01, step=0.01, format="%.3f")
    
    with st.sidebar.expander("Material Properties"):
        UTS = st.number_input('Ultimate Tensile Strength (UTS, MPa)', value=0.01, step=0.01, format="%.3f")
        Sy = st.number_input('Yield Strength (Sy, MPa)', value=0.01, step=0.01, format="%.3f")
        a = st.number_input('Surface factor constant (a)', value=0.01, step=0.01, format="%.3f")
        b = st.number_input('Surface factor exponent (b)', value=-0.01, step=0.01, format="%.3f")
    
    # Calculate geometric ratios for Kt
    Dd_ratio = Da / Db if Db != 0 else 0
    rd_ratio = r / Db if Db != 0 else 0
    
    # Kt estimation (simplified - should be replaced with proper interpolation)
    Kt = 1.0 + 0.5*(Dd_ratio-1)*(1 + 1/math.sqrt(rd_ratio)) if rd_ratio > 0 else 1.0
    
    data = {
        'Da (mm)': Da, 'Db (mm)': Db, 'L (mm)': L, 'r (mm)': r,
        'Fa (N)': Fa, 'Fb (N)': Fb, 'Lfa (mm)': Lfa, 'Lfb (mm)': Lfb,
        'Mean Load (N)': mean_load, 'Amplitude Load (N)': amplitude_load,
        'UTS (MPa)': UTS, 'Sy (MPa)': Sy, 'a': a, 'b': b, 'Kt': Kt
    }
    
    return pd.DataFrame(data, index=[0])

# Calculations
def perform_calculations(df):
    # Extract values
    Da = df['Da (mm)'].values[0]
    Db = df['Db (mm)'].values[0]
    L = df['L (mm)'].values[0]
    r = df['r (mm)'].values[0]
    Fa = df['Fa (N)'].values[0]
    Fb = df['Fb (N)'].values[0]
    Lfa = df['Lfa (mm)'].values[0]
    Lfb = df['Lfb (mm)'].values[0]
    mean_load = df['Mean Load (N)'].values[0]
    amplitude_load = df['Amplitude Load (N)'].values[0]
    UTS = df['UTS (MPa)'].values[0]
    Sy = df['Sy (MPa)'].values[0]
    a = df['a'].values[0]
    b = df['b'].values[0]
    Kt = df['Kt'].values[0]
    
    # Core calculations
    results = {}
    
    # Fatigue strength calculations
    results['Se_prime (MPa)'] = 0.5 * UTS
    results['ka'] = a * (UTS ** b)
    results['kb'] = 1.24 * (Da ** -0.107) if 7.62 <= Da <= 51 else 1.51 * (Da ** -0.157)
    results['Se (MPa)'] = results['ka'] * results['kb'] * results['Se_prime (MPa)']
    
    # Neuber's constant
    if 340 <= UTS <= 1700:
        results['NC (√mm)'] = 1.24 - 2.25e-3*UTS + 1.60e-6*(UTS**2) - 4.11e-10*(UTS**3)
    else:
        results['NC (√mm)'] = None
    
    # Stress concentration
    if 'NC (√mm)' in results and results['NC (√mm)'] is not None and r > 0:
        results['Kf'] = 1 + (Kt - 1)/(1 + results['NC (√mm)']/math.sqrt(r))
    else:
        results['Kf'] = None
    
    # Bending moment and stress
    results['M_B (N·mm)'] = (Lfa * Fb / L) - 250 if L != 0 else 0
    results['Section Modulus (mm³)'] = (math.pi * Db**3) / 32
    
    # Stress calculations
    if results['Kf'] is not None and results['Section Modulus (mm³)'] > 0:
        results['σ_ar (MPa)'] = results['Kf'] * results['M_B (N·mm)'] / results['Section Modulus (mm³)']
    else:
        results['σ_ar (MPa)'] = None
    
    # Maximum and minimum stress calculations
    if results['Section Modulus (mm³)'] > 0:
        results['σ_max (MPa)'] = (mean_load + amplitude_load) / results['Section Modulus (mm³)']
        results['σ_min (MPa)'] = (mean_load - amplitude_load) / results['Section Modulus (mm³)']
        results['σ_mean (MPa)'] = mean_load / results['Section Modulus (mm³)']
        results['σ_amp (MPa)'] = amplitude_load / results['Section Modulus (mm³)']
    else:
        results['σ_max (MPa)'] = None
        results['σ_min (MPa)'] = None
        results['σ_mean (MPa)'] = None
        results['σ_amp (MPa)'] = None
    
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
    'Parameter': ['Kt', 'Fatigue Kf', 'Bending Moment', 
                 'Section Modulus', 'Alternating Stress',
                 'Maximum Stress', 'Minimum Stress',
                 'Mean Stress', 'Stress Amplitude'],
    'Value': [
        formatted_results.get('Kt', 'N/A'),
        formatted_results.get('Kf', 'N/A'),
        formatted_results.get('M_B (N·mm)', 'N/A'),
        formatted_results.get('Section Modulus (mm³)', 'N/A'),
        formatted_results.get('σ_ar (MPa)', 'N/A'),
        formatted_results.get('σ_max (MPa)', 'N/A'),
        formatted_results.get('σ_min (MPa)', 'N/A'),
        formatted_results.get('σ_mean (MPa)', 'N/A'),
        formatted_results.get('σ_amp (MPa)', 'N/A')
    ],
    'Units': ['-', '-', 'N·mm', 'mm³', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa']
}
st.table(pd.DataFrame(stress_results))

# Safety factor calculation
if results['σ_ar (MPa)'] is not None and results['Se (MPa)'] is not None:
    safety_factor = results['Se (MPa)'] / results['σ_ar (MPa)']
    st.metric("Safety Factor Against Fatigue Failure", value=f"{safety_factor:.3f}")
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

