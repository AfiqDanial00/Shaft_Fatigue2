# FatigPro - Updated Streamlit App for Shaft Fatigue Evaluation
import streamlit as st
import pandas as pd
import math
import numpy as np

# Configure page
st.set_page_config(layout="wide", page_title="FatigPro-Advanced Shaft Fatigue Failure Evaluation")

# Main header
st.header("FatigPro-Advanced Shaft Fatigue Failure Evaluation")

# [Previous code remains the same until the results display section...]

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

# Finite Life Results Only
st.subheader("Finite Life Results")
if calc_results.get('Cycles to Failure N'):
    st.table(pd.DataFrame({
        'Parameter': ['a', 'b', 'Cycles to Failure (N)'],
        'Value': [
            f"{calc_results['Finite Life a']:.1f" if calc_results['Finite Life a'] else 'N/A',
            f"{calc_results['Finite Life b']:.4f" if calc_results['Finite Life b'] else 'N/A',
            f"{calc_results['Cycles to Failure N']/1000:.1f} × 10³" if calc_results['Cycles to Failure N'] else 'N/A'
        ],
        'Units': ['MPa', '-', 'cycles']
    }))
else:
    st.info("Finite life calculations not applicable (stress is below endurance limit or above yield strength)")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Input Parameters",
    convert_df(input_df),
    file_name="shaft_parameters.csv",
    mime="text/csv"
)
