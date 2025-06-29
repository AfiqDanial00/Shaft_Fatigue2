# Add this modification in the results display section (replace the existing safety factor display)

# ... (previous code remains the same)

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

# Modified Safety Factor Display with Safety Check
if calc_results['Safety Factor'] is not None:
    n = calc_results['Safety Factor']
    st.metric("Safety Factor (Modified Goodman)", f"{n:.3f}")
    
    # Determine if shaft is safe
    if n > 1.0:
        st.success("✅ Shaft is SAFE (Safety Factor > 1.0)")
    elif n == 1.0:
        st.warning("⚠️ Shaft is at CRITICAL LIMIT (Safety Factor = 1.0)")
    else:
        st.error("❌ Shaft is UNSAFE (Safety Factor < 1.0)")
else:
    st.warning("⚠️ Unable to calculate Safety Factor. Check inputs.")

# ... (rest of the code remains the same)
