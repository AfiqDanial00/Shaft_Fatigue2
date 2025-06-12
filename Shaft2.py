import streamlit as st
import pandas as pd
import math
from PIL import Image
import os
from glob import glob

# Page configuration
st.set_page_config(page_title="Shaft Fatigue Evaluator", page_icon="⚙️", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        max-width: 1200px;
    }
    .header {
        color: #2E86AB;
    }
    .section {
        background-color: #F5F5F5;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-box {
        background-color: #E8F4F8;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .warning {
        color: #FF6B35;
        font-weight: bold;
    }
    .success {
        color: #4CAF50;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("⚙️ Advanced Shaft Fatigue Evaluation")
st.markdown("""
This tool evaluates shaft fatigue life based on Shigley's Mechanical Engineering Design principles.
""")

# Sidebar for input parameters
with st.sidebar:
    st.header("📋 Input Parameters")
    st.subheader("Shaft Dimensions")
    shaft_diameter_A = st.number_input('Major Diameter (Da), mm', min_value=0.01, value=30.0, step=1.0)
    shaft_diameter_B = st.number_input('Minor Diameter (Db), mm', min_value=0.01, value=20.0, step=1.0)
    shaft_length = st.number_input('Shaft Length (L), mm', min_value=0.01, value=500.0, step=10.0)
    fillet_radius = st.number_input('Fillet Radius (r), mm', min_value=0.01, value=2.0, step=0.5)
    
    st.subheader("Loading Conditions")
    Applied_Force_at_Point_A = st.number_input('Force at A (Fa), N', min_value=0.01, value=1000.0, step=100.0)
    Applied_Force_at_Point_B = st.number_input('Force at B (Fb), N', min_value=0.01, value=800.0, step=100.0)
    Length_from_Fa_to_shaft_end = st.number_input('Distance Fa to end (Lfa), mm', min_value=0.01, value=100.0, step=10.0)
    Length_from_Fb_to_shaft_end = st.number_input('Distance Fb to end (Lfb), mm', min_value=0.01, value=150.0, step=10.0)
    
    st.subheader("Material Properties")
    UTS = st.number_input('Ultimate Tensile Strength (UTS), MPa', min_value=0.01, value=600.0, step=50.0)
    Sy = st.number_input('Yield Strength (Sy), MPa', min_value=0.01, value=450.0, step=50.0)
    
    st.subheader("Surface & Notch Factors")
    surface_finish = st.selectbox("Surface Finish", 
                                ["Ground", "Machined", "Cold-drawn", "Hot-rolled", "As-forged"])
    Constant_a_for_ka = st.number_input('Marin Factor (a)', value=4.51, format="%.4f")
    Constant_b_for_ka = st.number_input('Marin Factor (b)', value=-0.265, format="%.4f")
    Kt = st.number_input('Stress Concentration Factor (Kt)', min_value=1.0, value=1.5, step=0.1)

# Display shaft diagram
st.subheader("📐 Shaft Diagram")
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image("https://homework.study.com/cimages/multimages/16/060519-118885225862519178792.jpg", 
             caption="Fig. 1: Schematic of Stepped Shaft with Dimensions", use_column_width=True)

# Calculations
with st.expander("🔍 View Calculation Details", expanded=False):
    st.markdown("### Fatigue Analysis Methodology")
    st.markdown("""
    This analysis follows Shigley's Mechanical Engineering Design approach for fatigue evaluation:
    1. Calculate endurance limit modification factors
    2. Determine corrected endurance limit
    3. Calculate stress concentration factors
    4. Evaluate alternating and mean stresses
    5. Apply fatigue failure criteria (Goodman, Gerber, etc.)
    """)

# Section 1: Basic Calculations
st.markdown("## 📊 Basic Calculations")
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate Se'
        Se_prime = 0.5 * UTS
        st.markdown(f"**Endurance Limit (Se'):** {Se_prime:.2f} MPa")
        st.caption("Se' = 0.5 × UTS (for steels)")
        
        # Calculate ka (surface factor)
        ka = Constant_a_for_ka * (UTS ** Constant_b_for_ka)
        st.markdown(f"**Surface Factor (ka):** {ka:.4f}")
        st.caption(f"ka = {Constant_a_for_ka} × (UTS)^{Constant_b_for_ka}")
        
        # Calculate kb (size factor)
        if 7.62 <= shaft_diameter_A <= 51:
            kb = 1.24 * (shaft_diameter_A ** -0.107)
        elif 51 < shaft_diameter_A <= 254:
            kb = 1.51 * (shaft_diameter_A ** -0.157)
        else:
            kb = None
            st.error("Size factor kb cannot be calculated: Diameter out of range (7.62-254 mm)")
        
        if kb is not None:
            st.markdown(f"**Size Factor (kb):** {kb:.4f}")
            st.caption("For bending and torsion of rotating shafts")
            
            # Calculate Se (corrected endurance limit)
            Se = ka * kb * Se_prime
            st.markdown(f"**Corrected Endurance Limit (Se):** {Se:.2f} MPa")
            st.caption("Se = ka × kb × Se'")
    
    with col2:
        # Calculate Neuber Constant
        if 340 <= UTS <= 1700:
            NC = 1.24 - 2.25e-3*UTS + 1.60e-6*(UTS**2) - 4.11e-10*(UTS**3)
            st.markdown(f"**Neuber Constant (√mm):** {NC:.4f}")
            st.caption("For steels with UTS between 340-1700 MPa")
            
            # Calculate Kf (fatigue stress concentration factor)
            if fillet_radius > 0:
                Kf = 1 + (Kt - 1) / (1 + NC / math.sqrt(fillet_radius))
                st.markdown(f"**Fatigue Stress Concentration Factor (Kf):** {Kf:.4f}")
                st.caption(f"Kf = 1 + (Kt-1)/(1 + NC/√r)")
            else:
                st.error("Cannot calculate Kf: Fillet radius must be > 0")
        else:
            st.error("Cannot calculate Neuber Constant: UTS must be between 340-1700 MPa")

# Section 2: Stress Calculations
st.markdown("## 📈 Stress Analysis")
with st.container():
    st.subheader("Bending Stresses")
    
    # Calculate bending moments
    Ma = Applied_Force_at_Point_A * Length_from_Fa_to_shaft_end
    Mb = Applied_Force_at_Point_B * Length_from_Fb_to_shaft_end
    M_max = max(Ma, Mb)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Bending Moment at A:** {Ma:.2f} N-mm")
        st.markdown(f"**Bending Moment at B:** {Mb:.2f} N-mm")
        st.markdown(f"**Maximum Bending Moment:** {M_max:.2f} N-mm")
    
    with col2:
        # Calculate section properties
        I_A = math.pi * shaft_diameter_A**4 / 64
        I_B = math.pi * shaft_diameter_B**4 / 64
        c_A = shaft_diameter_A / 2
        c_B = shaft_diameter_B / 2
        
        st.markdown(f"**Moment of Inertia (A):** {I_A:.2e} mm⁴")
        st.markdown(f"**Moment of Inertia (B):** {I_B:.2e} mm⁴")
    
    # Calculate bending stresses
    sigma_A = M_max * c_A / I_A if I_A > 0 else 0
    sigma_B = M_max * c_B / I_B if I_B > 0 else 0
    sigma_max = max(sigma_A, sigma_B)
    
    st.markdown(f"**Maximum Bending Stress:** {sigma_max:.2f} MPa", help="σ = Mc/I")
    
    # Calculate alternating and mean stresses (assuming fully reversed loading)
    sigma_a = sigma_max  # fully reversed
    sigma_m = 0          # no mean stress
    
    st.markdown("### Stress Components")
    st.markdown(f"**Alternating Stress (σₐ):** {sigma_a:.2f} MPa")
    st.markdown(f"**Mean Stress (σₘ):** {sigma_m:.2f} MPa")

# Section 3: Fatigue Analysis
st.markdown("## 🔄 Fatigue Life Assessment")
with st.container():
    st.subheader("Modified Goodman Criterion")
    
    if 'Se' in locals() and Se > 0 and UTS > 0:
        # Goodman line calculation
        goodman_ratio = (sigma_a / Se) + (sigma_m / UTS)
        safety_factor_goodman = 1 / goodman_ratio if goodman_ratio > 0 else float('inf')
        
        st.markdown(f"**Goodman Ratio:** {goodman_ratio:.4f}")
        st.markdown(f"**Safety Factor (Goodman):** {safety_factor_goodman:.2f}")
        
        if goodman_ratio < 1:
            st.success("✅ Design is safe according to Goodman criterion")
        else:
            st.warning("⚠️ Design may fail according to Goodman criterion")
    
    st.subheader("Gerber Criterion")
    if 'Se' in locals() and Se > 0 and UTS > 0:
        gerber_ratio = (sigma_a / Se) + (sigma_m / UTS)**2
        safety_factor_gerber = 1 / gerber_ratio if gerber_ratio > 0 else float('inf')
        
        st.markdown(f"**Gerber Ratio:** {gerber_ratio:.4f}")
        st.markdown(f"**Safety Factor (Gerber):** {safety_factor_gerber:.2f}")
        
        if gerber_ratio < 1:
            st.success("✅ Design is safe according to Gerber criterion")
        else:
            st.warning("⚠️ Design may fail according to Gerber criterion")

# Section 4: Results Summary
st.markdown("## 📝 Summary of Results")
results = {
    "Parameter": [
        "Material UTS", "Material Yield Strength", 
        "Corrected Endurance Limit (Se)", 
        "Maximum Bending Stress", 
        "Goodman Safety Factor", 
        "Gerber Safety Factor"
    ],
    "Value": [
        f"{UTS:.2f} MPa", f"{Sy:.2f} MPa",
        f"{Se:.2f} MPa" if 'Se' in locals() else "N/A",
        f"{sigma_max:.2f} MPa",
        f"{safety_factor_goodman:.2f}" if 'safety_factor_goodman' in locals() else "N/A",
        f"{safety_factor_gerber:.2f}" if 'safety_factor_gerber' in locals() else "N/A"
    ],
    "Status": [
        "", "",
        "",
        "⚠️ Critical" if sigma_max > Sy else "✅ OK",
        "✅ Safe" if 'safety_factor_goodman' in locals() and safety_factor_goodman > 1 else "⚠️ Check",
        "✅ Safe" if 'safety_factor_gerber' in locals() and safety_factor_gerber > 1 else "⚠️ Check"
    ]
}

results_df = pd.DataFrame(results)
st.dataframe(results_df, hide_index=True, use_container_width=True)

# References and additional resources
st.markdown("---")
st.markdown("### 📚 References")
st.markdown("""
- Shigley's Mechanical Engineering Design, 10th Edition
- Budynas & Nisbett: Machine Component Design
- Juvinall & Marshek: Fundamentals of Machine Component Design
""")

# Footer
st.markdown("---")
st.markdown("""
**Note:** This tool provides preliminary fatigue analysis only. 
For critical applications, always verify with detailed engineering analysis.
""")
