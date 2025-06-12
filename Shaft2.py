import streamlit as st
import pandas as pd
import math
from PIL import Image
import os
from glob import glob


# Configure page
st.set_page_config(
    page_title="Shaft Fatigue Analyzer Pro",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .header-style {
        font-size: 20px;
        font-weight: bold;
        color: #2E86AB;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 5px solid #FFC107;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #D4EDDA;
        border-left: 5px solid #28A745;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .tab-content {
        padding-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.title("⚙️ Shaft Fatigue Analyzer Pro")
st.markdown("""
*Comprehensive fatigue analysis for rotating shafts based on Shigley's Mechanical Engineering Design principles*
""")

# Sidebar configuration
with st.sidebar:
    st.header("🔧 Input Parameters")
    
    with st.expander("📐 Geometry", expanded=True):
        Da = st.number_input('Major Diameter (Da, mm)', min_value=0.1, value=38.0, step=0.1)
        Db = st.number_input('Minor Diameter (Db, mm)', min_value=0.1, value=32.0, step=0.1)
        r = st.number_input('Fillet Radius (r, mm)', min_value=0.1, value=3.0, step=0.1,
                          help="Radius at the shoulder fillet")
        L = st.number_input('Shaft Length (L, mm)', min_value=0.1, value=550.0, step=1.0)
        Lfa = st.number_input('Fa Location (Lfa, mm)', min_value=0.0, value=225.0, step=1.0)
        Lfb = st.number_input('Fb Location (Lfb, mm)', min_value=0.0, value=300.0, step=1.0)
    
    with st.expander("🔩 Material", expanded=True):
        material_type = st.selectbox("Material Type", 
                                   ["Steel", "Aluminum", "Titanium", "Custom"])
        UTS = st.number_input('Tensile Strength (UTS, MPa)', min_value=100.0, value=690.0, step=10.0)
        Sy = st.number_input('Yield Strength (Sy, MPa)', min_value=100.0, value=490.0, step=10.0)
        
        if material_type == "Steel":
            a, b = 4.51, -0.265
        elif material_type == "Aluminum":
            a, b = 4.51, -0.265  # Placeholder - use actual values
        else:
            a = st.number_input('Surface Factor (a)', value=4.51, step=0.01)
            b = st.number_input('Surface Exponent (b)', value=-0.265, step=0.001)
    
    with st.expander("📊 Loading", expanded=True):
        Fa = st.number_input('Force at A (Fa, N)', value=1000.0, step=10.0)
        Fb = st.number_input('Force at B (Fb, N)', value=1500.0, step=10.0)
        load_type = st.selectbox("Loading Type", 
                                ["Rotating", "Reversed", "Fluctuating"])
        
    # Calculate Kt based on geometry
    D_ratio = Da / Db
    r_ratio = r / Db
    Kt = 1.0 + 0.5*(D_ratio-1)*(1 + 1/math.sqrt(r_ratio))

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Results", "📐 Diagrams", "📈 Stress Analysis", "📝 Report"])

with tab1:
    st.markdown('<div class="header-style">Fatigue Analysis Results</div>', unsafe_allow_html=True)
    
    # Perform calculations
    Se_prime = 0.5 * UTS
    ka = a * (UTS ** b)
    kb = 1.24 * (Da ** -0.107) if 7.62 <= Da <= 51 else 1.51 * (Da ** -0.157)
    Se = ka * kb * Se_prime
    
    # Neuber's constant
    if 340 <= UTS <= 1700:
        NC = 1.24 - 2.25e-3*UTS + 1.60e-6*(UTS**2) - 4.11e-10*(UTS**3)
    else:
        NC = None
    
    # Stress concentration
    if NC is not None:
        Kf = 1 + (Kt - 1)/(1 + NC/math.sqrt(r))
    else:
        Kf = None
    
    # Bending moment and stress
    M_B = (Lfa * Fb / L) - 250  # Simplified calculation
    section_modulus = (math.pi * Db**3) / 32
    sigma_ar = Kf * M_B / section_modulus if Kf is not None else None
    
    # Display in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">'
                   '<h3>Endurance Limit</h3>'
                   f'<p style="font-size:24px;text-align:center;">{Se:.1f} MPa</p>'
                   '</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">'
                   '<h3>Surface Factor</h3>'
                   f'<p style="font-size:24px;text-align:center;">{ka:.3f}</p>'
                   '</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">'
                   '<h3>Stress Concentration</h3>'
                   f'<p style="font-size:24px;text-align:center;">Kf = {Kf:.2f}</p>'
                   '</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">'
                   '<h3>Size Factor</h3>'
                   f'<p style="font-size:24px;text-align:center;">{kb:.3f}</p>'
                   '</div>', unsafe_allow_html=True)
    
    with col3:
        if sigma_ar is not None:
            safety_factor = Se / sigma_ar
            status = "success" if safety_factor > 1.5 else "warning"
            
            st.markdown(f'<div class="metric-card">'
                       f'<h3>Safety Factor</h3>'
                       f'<p style="font-size:24px;text-align:center;color:{"#28A745" if safety_factor > 1.5 else "#DC3545"};">'
                       f'{safety_factor:.2f}</p>'
                       f'<p style="text-align:center;">{"✅ Safe" if safety_factor > 1.5 else "⚠️ Marginal"}</p>'
                       '</div>', unsafe_allow_html=True)
        else:
            st.warning("Cannot calculate safety factor")
        
        st.markdown('<div class="metric-card">'
                   '<h3>Alternating Stress</h3>'
                   f'<p style="font-size:24px;text-align:center;">{sigma_ar:.1f} MPa</p>'
                   '</div>', unsafe_allow_html=True)
    
    # Detailed results table
    with st.expander("📋 Detailed Calculation Results"):
        results_data = {
            "Parameter": ["Material UTS", "Material Yield", "Endurance Limit (Se')",
                         "Surface Factor (ka)", "Size Factor (kb)", "Corrected Se",
                         "Theoretical Kt", "Fatigue Kf", "Bending Moment",
                         "Alternating Stress", "Safety Factor"],
            "Value": [f"{UTS:.1f} MPa", f"{Sy:.1f} MPa", f"{Se_prime:.1f} MPa",
                     f"{ka:.3f}", f"{kb:.3f}", f"{Se:.1f} MPa",
                     f"{Kt:.2f}", f"{Kf:.2f}" if Kf else "N/A",
                     f"{M_B:.1f} N·mm", f"{sigma_ar:.1f} MPa" if sigma_ar else "N/A",
                     f"{safety_factor:.2f}" if sigma_ar else "N/A"],
            "Description": ["Ultimate tensile strength", "Yield strength",
                           "0.5 × UTS", f"{a} × UTS^{b}", "Size correction",
                           "ka × kb × Se'", "Theoretical stress concentration",
                           "Fatigue stress concentration", "Maximum bending moment",
                           "Kf × σ_nominal", "Se / σ_ar"]
        }
        
        st.table(pd.DataFrame(results_data))

with tab2:
    st.markdown('<div class="header-style">Reference Diagrams</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://homework.study.com/cimages/multimages/16/060519-118885225862519178792.jpg",
                caption="Shaft Geometry and Dimensions", use_column_width=True)
        
    with col2:
        st.image("https://www.researchgate.net/publication/44220429/figure/download/fig1/AS:670016391356455@1536755764941/Notch-sensitivity-versus-notch-radius-for-steels-and-aluminium-alloys.png",
                caption="Notch Sensitivity Chart", use_column_width=True)
    
    st.image("https://www.engineersedge.com/materials/images/stress-concentration-2.png",
            caption="Stress Concentration Factors", use_column_width=True)

with tab3:
    st.markdown('<div class="header-style">Stress Analysis</div>', unsafe_allow_html=True)
    
    # Stress distribution visualization placeholder
    st.write("""
    ### Stress Distribution
    *Visualization of stress distribution along the shaft*
    """)
    
    # Placeholder for stress plot
    st.image("https://www.researchgate.net/publication/334382089/figure/fig1/AS:779505091674112@1562840064698/Stress-distribution-in-a-stepped-shaft-with-fillet-radius.png",
             caption="Example stress distribution in a stepped shaft", width=600)
    
    # Critical locations
    st.write("""
    ### Critical Locations
    1. **Fillet Transition**: Highest stress concentration
    2. **Load Application Points**: High bending moments
    3. **Surface Defects**: Potential crack initiation sites
    """)

with tab4:
    st.markdown('<div class="header-style">Analysis Report</div>', unsafe_allow_html=True)
    
    # Generate report
    st.write(f"""
    ## Shaft Fatigue Analysis Report
    
    ### 1. Shaft Geometry
    - Major Diameter (Da): {Da:.1f} mm
    - Minor Diameter (Db): {Db:.1f} mm
    - Fillet Radius (r): {r:.1f} mm
    - Shaft Length (L): {L:.1f} mm
    
    ### 2. Material Properties
    - Material Type: {material_type}
    - Ultimate Tensile Strength: {UTS:.1f} MPa
    - Yield Strength: {Sy:.1f} MPa
    
    ### 3. Loading Conditions
    - Force at A (Fa): {Fa:.1f} N
    - Force at B (Fb): {Fb:.1f} N
    - Loading Type: {load_type}
    
    ### 4. Fatigue Analysis Results
    - Corrected Endurance Limit (Se): {Se:.1f} MPa
    - Alternating Stress (σ_ar): {sigma_ar:.1f} MPa
    - Safety Factor: {safety_factor:.2f}
    
    ### 5. Conclusions
    The shaft design is {"safe" if safety_factor > 1.5 else "potentially unsafe"} 
    for the specified loading conditions with a safety factor of {safety_factor:.2f}.
    """)
    
    # Download button
    st.download_button(
        label="📥 Download Full Report",
        data=f"Shaft Fatigue Analysis Report\n\n" +
             f"Shaft Geometry:\nDa={Da}mm, Db={Db}mm, r={r}mm\n\n" +
             f"Material: {material_type}, UTS={UTS}MPa, Sy={Sy}MPa\n\n" +
             f"Results:\nSe={Se:.1f}MPa, SF={safety_factor:.2f}",
        file_name="shaft_fatigue_report.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown("""
*Disclaimer: This tool provides preliminary analysis only. For critical applications, 
consult a qualified mechanical engineer and perform detailed FEA analysis.*
""")
