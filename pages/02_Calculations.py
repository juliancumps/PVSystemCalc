import streamlit as st

st.header("Calculations:")
st.markdown("###### Please be sure to click all calculation buttons in order from top to bottom to ensure correct calculations.")
st.markdown("###### You may also expand the Calculation Details box to view the math itself.")
st.divider()

if 'voc' not in st.session_state:
    st.warning("Please fill in the Inputs page first!")
else:
    st.subheader("Calculate Voc Increase @ Coldest Temperature")
    
    if st.button("Calculate Voc Increase"):
        # Convert tcold from Fahrenheit to Celsius
        tcold_celsius = (st.session_state.tcold - 32) * 5/9
        
        # Calculate delta temp
        stc = 25
        delta_temp = tcold_celsius - stc
        
        # Convert temperature coefficient from percentage to decimal
        temp_coeff_decimal = st.session_state.tempCoeff / 100
        
        # Calculate Voc increase
        voc_increase = st.session_state.voc * temp_coeff_decimal * delta_temp
        voc_cold = st.session_state.voc + voc_increase
        
        # Store voc_cold in session state for future calculations
        st.session_state.voc_cold = voc_cold
        
        # Display the result
        st.success(f"**Result:** Voc at cold temperature: {voc_cold:.2f} V")
        
        # Dropdown to show the math
        with st.expander("Show Calculation Details"):
            st.write("**Step 1: Convert Tcold from Fahrenheit to Celsius**")
            st.latex(r"T_{cold}°C = (T_{cold}°F - 32) \times \frac{5}{9}")
            st.write(f"T_cold°C = ({st.session_state.tcold} - 32) × 5/9 = **{tcold_celsius:.2f}°C**")
            
            st.write("**Step 2: Calculate ΔT (Delta Temperature)**")
            st.latex(r"\Delta T = T_{cold}°C - T_{STC}")
            st.write(f"ΔT = {tcold_celsius:.2f} - {stc} = **{delta_temp:.2f}°C**")
            
            st.write("**Step 3: Convert Temperature Coefficient to Decimal**")
            st.write(f"Temp Coeff (decimal) = {st.session_state.tempCoeff}% / 100 = **{temp_coeff_decimal}**")
            
            st.write("**Step 4: Calculate Voc Increase**")
            st.latex(r"V_{oc,increase} = V_{oc} \times \text{Temp Coeff (decimal)} \times \Delta T")
            st.write(f"V_oc,increase = {st.session_state.voc} × {temp_coeff_decimal} × {delta_temp:.2f} = **{voc_increase:.2f} V**")
            
            st.write("**Step 5: Calculate Final Voc at Cold Temperature**")
            st.latex(r"V_{oc,cold} = V_{oc} + V_{oc,increase}")
            st.write(f"V_oc,cold = {st.session_state.voc} + {voc_increase:.2f} = **{voc_cold:.2f} V**")
    
    st.divider()
    
    st.subheader("Calculate Max Series and Parallel Configuration")
    
    if st.button("Calculate Max Series/Parallel Panels"):
        # Use voc_cold if available, otherwise use regular voc
        voc_to_use = st.session_state.get('voc_cold', st.session_state.voc)
        
        # Calculate max panels in series
        max_series = int(st.session_state.maxV / voc_to_use)
        
        # Calculate max panels in parallel
        max_parallel = int(st.session_state.macA / st.session_state.isc)
        
        st.session_state.max_series = max_series
        st.session_state.max_parallel = max_parallel
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"**Max Panels in Series:** {max_series} panels")
        
        with col2:
            st.success(f"**Max Panels in Parallel:** {max_parallel} strings")
        
        # Show calculation details
        with st.expander("Show Calculation Details"):
            st.write("**Series Calculation:**")
            st.latex(r"N_{series} = \left\lfloor \frac{V_{max}}{V_{oc,cold}} \right\rfloor")
            st.write(f"N_series = {st.session_state.maxV} ÷ {voc_to_use:.2f} = **{max_series} panels**")
            st.info(f"Using Voc at cold temperature ({voc_to_use:.2f} V) for safety margin")
            
            st.write("**Parallel Calculation:**")
            st.latex(r"N_{parallel} = \left\lfloor \frac{I_{max}}{I_{sc}} \right\rfloor")
            st.write(f"N_parallel = {st.session_state.macA} ÷ {st.session_state.isc} = **{max_parallel} panels**")

            st.divider()

st.subheader("Calculate Max Panels Based on Power Rating")

# System voltage selection
system_voltage = st.radio("Select Your System Voltage:", options=["12V", "24V", "48V"], horizontal=True)

# Map voltage to nominal power
voltage_map = {
    "12V": st.session_state.nominalpv12,
    "24V": st.session_state.nominalpv24,
    "48V": st.session_state.nominalpv48
}

nominal_power = voltage_map[system_voltage]

if st.button("Calculate Max Panels by Power"):
    # Calculate max panels based on power rating
    max_panels_power = int(nominal_power / st.session_state.ppp)
    
    st.session_state.system_voltage = system_voltage
    st.session_state.nominal_power = nominal_power
    st.session_state.max_panels_power = max_panels_power
    
    st.success(f"**Theoretical Max Panels (Power Limited):** {max_panels_power} panels")
    
    with st.expander("Show Calculation Details"):
        st.write(f"**System Voltage Selected:** {system_voltage}")
        st.write(f"**Nominal PV Power Limit:** {nominal_power} W")
        st.latex(r"N_{panels,power} = \left\lfloor \frac{P_{nominal}}{P_{panel}} \right\rfloor")
        st.write(f"N_panels,power = {nominal_power} ÷ {st.session_state.ppp} = **{max_panels_power} panels**")

st.divider()

st.subheader("Find Safe Panel Configuration")

if st.button("Find Valid Configurations"):
    if 'max_series' not in st.session_state or 'max_panels_power' not in st.session_state:
        st.warning("Please complete the previous calculations first!")
    else:
        # Get all constraints
        max_series = st.session_state.max_series
        max_parallel = st.session_state.max_parallel
        max_panels_power = st.session_state.max_panels_power
        battery_voltage = st.session_state.battery_voltage
        max_charge_current = st.session_state.macA
        
        # Panel specs
        voc_cold = st.session_state.get('voc_cold', st.session_state.voc)
        isc = st.session_state.isc
        ppp = st.session_state.ppp
        
        # Generate all valid configurations
        valid_configs = []
        
        for series in range(1, max_series + 1):
            for parallel in range(1, max_parallel + 1):
                total_panels = series * parallel
                
                # Check power constraint
                if total_panels > max_panels_power:
                    continue
                
                # Calculate output specs from solar panels into MPPT
                output_voltage = voc_cold * series
                output_current = isc * parallel
                output_power = ppp * total_panels
                
                # Check if output current exceeds charger limit
                if output_current > max_charge_current:
                    pass_current_check = False
                else:
                    pass_current_check = True
                
                # All constraints must pass
                passes_all = pass_current_check
                
                valid_configs.append({
                    "Series": series,
                    "Parallel": parallel,
                    "Config": f"{series}s{parallel}p",
                    "Total Panels": total_panels,
                    "Status": "Safe" if passes_all else "Unsafe",
                    "Output Voltage (V)": round(output_voltage, 2),
                    "Output Current (A)": round(output_current, 2),
                    "Output Power (W)": output_power,
                    "Max Current Limit (A)": max_charge_current
                })
        
        if valid_configs:
            import pandas as pd
            df = pd.DataFrame(valid_configs)
            
            # Sort by Total Panels descending (most panels first)
            df = df.sort_values(by='Total Panels', ascending=False).reset_index(drop=True)
            
            safe_count = len([c for c in valid_configs if c['Status'] == "Safe"])
            st.success(f"Found {safe_count} potentially safe configuration(s)!")
            
            # Color entire rows based on Status
            def highlight_row(row):
                if row['Status'] == "Safe":
                    return ['background-color: #90EE90'] * len(row)
                else:
                    return ['background-color: #FFB6C6'] * len(row)
            
            styled_df = df.style.apply(highlight_row, axis=1)
            styled_df = styled_df.set_properties(**{'color': 'black'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            with st.expander("Show Calculation Details"):
                st.write("**Output Voltage (into MPPT):**")
                st.latex(r"V_{output} = V_{oc,cold} \times N_{series}")
                st.write("**Output Current (into MPPT):**")
                st.latex(r"I_{output} = I_{sc} \times N_{parallel}")
                st.write(f"And the output current must be ≤ {max_charge_current} A (charger limit)")
                st.info("Green rows are safe configurations. Red rows exceed the charger's current limit.")
        else:
            st.error("No valid configurations found that meet all constraints!")

        st.divider()

st.subheader("Final Safety Check: Battery Output Current")

st.info("⚠️⚠️ **IMPORTANT:** Click this button to perform the final safety check. The MPPT controller will convert the solar panel voltage to match your battery voltage. During this conversion, the current will change to maintain power conservation. We must verify the output current to the battery does NOT exceed the charger's maximum current rating.")

if st.button("Perform Final Safety Check"):
    if 'max_series' not in st.session_state or 'max_panels_power' not in st.session_state:
        st.warning("Please complete the previous calculations first!")
    else:
        # Get all constraints
        max_series = st.session_state.max_series
        max_parallel = st.session_state.max_parallel
        max_panels_power = st.session_state.max_panels_power
        battery_voltage = st.session_state.battery_voltage
        max_charge_current = st.session_state.macA
        
        # Panel specs
        voc_cold = st.session_state.get('voc_cold', st.session_state.voc)
        isc = st.session_state.isc
        ppp = st.session_state.ppp
        
        # Generate all valid configurations
        final_configs = []
        
        for series in range(1, max_series + 1):
            for parallel in range(1, max_parallel + 1):
                total_panels = series * parallel
                
                # Check power constraint
                if total_panels > max_panels_power:
                    continue
                
                # Calculate output specs from solar panels into MPPT
                output_voltage = voc_cold * series
                output_current = isc * parallel
                output_power = ppp * total_panels
                
                # Check if output current from panels exceeds charger limit
                if output_current > max_charge_current:
                    continue
                
                # Calculate output current from MPPT to battery
                # Power is conserved: P = V * I, so I_battery = P / V_battery
                battery_output_current = output_power / battery_voltage
                
                # Check if battery output current exceeds charger limit
                if battery_output_current > max_charge_current:
                    passes_all = False
                else:
                    passes_all = True
                
                final_configs.append({
                    "Config": f"{series}s{parallel}p",
                    "Total Panels": total_panels,
                    "Panel Voltage (V)": round(output_voltage, 2),
                    "Panel Current (A)": round(output_current, 2),
                    "Panel Power (W)": output_power,
                    "Battery Voltage (V)": battery_voltage,
                    "Battery Current (A)": round(battery_output_current, 2),
                    "Max Charger Current (A)": max_charge_current,
                    "Status": "✓ SAFE" if passes_all else "✗ UNSAFE"
                })
        
        if final_configs:
            import pandas as pd
            df = pd.DataFrame(final_configs)
            
            # Sort by Total Panels descending (most panels first)
            df = df.sort_values(by='Total Panels', ascending=False).reset_index(drop=True)
            
            safe_count = len([c for c in final_configs if c['Status'] == "✓ SAFE"])
            
            if safe_count > 0:
                st.success(f"**Found {safe_count} SAFE configuration(s) for your system!**")
            else:
                st.warning(f"No safe configurations found. All configurations exceed battery current limits.")
            
            # Color entire rows based on Status
            def highlight_row(row):
                if row['Status'] == "✓ SAFE":
                    return ['background-color: #90EE90'] * len(row)
                else:
                    return ['background-color: #FFB6C6'] * len(row)
            
            styled_df = df.style.apply(highlight_row, axis=1)
            styled_df = styled_df.set_properties(**{'color': 'black'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            with st.expander("Understanding the Calculation"):
                st.write("**How the MPPT Controller Works:**")
                st.write("The MPPT (Maximum Power Point Tracker) receives power from your solar panels at their natural voltage and current. It then converts this power to match your battery voltage while maintaining total power through the relationship: P = V × I")
                
                st.write("**Step 1: Solar Panel Output**")
                st.latex(r"V_{panels} = V_{oc,cold} \times N_{series}")
                st.latex(r"I_{panels} = I_{sc} \times N_{parallel}")
                st.latex(r"P_{total} = P_{panel} \times N_{total}")
                
                st.write("**Step 2: MPPT Voltage Conversion**")
                st.write(f"The MPPT converts the panel voltage to match your battery voltage ({battery_voltage}V)")
                
                st.write("**Step 3: Battery Output Current (Power Conservation)**")
                st.latex(r"I_{battery} = \frac{P_{total}}{V_{battery}}")
                st.write("Since power must be conserved, when voltage decreases, current must increase proportionally.")
                
                st.write("**Step 4: Safety Check**")
                st.write(f"The battery output current must NOT exceed the charger's maximum rating of {max_charge_current}A")
                st.latex(r"I_{battery} \leq I_{max,charger}")
                
                st.success("✓ Green rows = Safe configurations you can use for your system")
                st.error("✗ Red rows = Unsafe - would exceed charger current limits to battery")
        else:
            st.error("No valid configurations found that meet all constraints!")
