import streamlit as st
import json

# ============================================
# INITIALIZE SESSION STATE WITH DEFAULTS
# ============================================
if 'ppp' not in st.session_state:
    st.session_state.ppp = 410.0
if 'voc' not in st.session_state:
    st.session_state.voc = 37.41
if 'isc' not in st.session_state:
    st.session_state.isc = 13.90
if 'vmp' not in st.session_state:
    st.session_state.vmp = 31.38
if 'imp' not in st.session_state:
    st.session_state.imp = 13.07
if 'tempCoeff' not in st.session_state:
    st.session_state.tempCoeff = -0.254
if 'maxV' not in st.session_state:
    st.session_state.maxV = 150.0
if 'macA' not in st.session_state:
    st.session_state.macA = 60.0
if 'tcold' not in st.session_state:
    st.session_state.tcold = -10.0
if 'nominalpv12' not in st.session_state:
    st.session_state.nominalpv12 = 860.0
if 'nominalpv24' not in st.session_state:
    st.session_state.nominalpv24 = 1720.0
if 'nominalpv48' not in st.session_state:
    st.session_state.nominalpv48 = 3440.0
if 'battery_voltage' not in st.session_state:
    st.session_state.battery_voltage = 48.0
if 'stc' not in st.session_state:
    st.session_state.stc = 25

st.header("Solar Panel Info")
st.subheader("Input Information From Your Solar Panel Datasheet")

# ============================================
# JSON SAVE/LOAD SECTION
# ============================================

st.divider()
st.subheader("Configuration Management")

config_col1, config_col2, config_col3 = st.columns(3)

with config_col1:
    if st.button("Generate & Download JSON", use_container_width=True):
        # Collect all current input values
        config_data = {
            "solar_panel": {
                "power_per_panel_watts": st.session_state.ppp,
                "open_circuit_voltage_voc": st.session_state.voc,
                "short_circuit_current_isc": st.session_state.isc,
                "voltage_at_max_power_vmp": st.session_state.vmp,
                "current_at_max_power_imp": st.session_state.imp,
                "temperature_coefficient_voc": st.session_state.tempCoeff
            },
            "mppt_charger": {
                "max_pv_voltage": st.session_state.maxV,
                "max_charge_current_amps": st.session_state.macA,
                "coldest_temperature_fahrenheit": st.session_state.tcold,
                "nominal_pv_power_12v_watts": st.session_state.nominalpv12,
                "nominal_pv_power_24v_watts": st.session_state.nominalpv24,
                "nominal_pv_power_48v_watts": st.session_state.nominalpv48
            },
            "battery_system": {
                "battery_bank_nominal_voltage": st.session_state.battery_voltage
            }
        }
        
        # Convert to JSON string
        json_str = json.dumps(config_data, indent=2)
        
        # Create download button
        st.download_button(
            label="📥 Download Configuration",
            data=json_str,
            file_name="pv_system_config.json",
            mime="application/json"
        )

with config_col2:
    uploaded_file = st.file_uploader("Upload Configuration JSON", type="json")
    
    if uploaded_file is not None:
        try:
            # Read and parse the JSON
            config_data = json.load(uploaded_file)
            
            # Validate structure
            required_sections = ['solar_panel', 'mppt_charger', 'battery_system']
            if not all(section in config_data for section in required_sections):
                st.error("❌ File corrupted or invalid format")
            else:
                # Validate required keys
                required_solar = ['power_per_panel_watts', 'open_circuit_voltage_voc', 'short_circuit_current_isc', 
                                'voltage_at_max_power_vmp', 'current_at_max_power_imp', 'temperature_coefficient_voc']
                required_mppt = ['max_pv_voltage', 'max_charge_current_amps', 'coldest_temperature_fahrenheit',
                               'nominal_pv_power_12v_watts', 'nominal_pv_power_24v_watts', 'nominal_pv_power_48v_watts']
                required_battery = ['battery_bank_nominal_voltage']
                
                if (all(k in config_data['solar_panel'] for k in required_solar) and
                    all(k in config_data['mppt_charger'] for k in required_mppt) and
                    all(k in config_data['battery_system'] for k in required_battery)):
                    
                    # Load values into session state
                    st.session_state.ppp = config_data['solar_panel']['power_per_panel_watts']
                    st.session_state.voc = config_data['solar_panel']['open_circuit_voltage_voc']
                    st.session_state.isc = config_data['solar_panel']['short_circuit_current_isc']
                    st.session_state.vmp = config_data['solar_panel']['voltage_at_max_power_vmp']
                    st.session_state.imp = config_data['solar_panel']['current_at_max_power_imp']
                    st.session_state.tempCoeff = config_data['solar_panel']['temperature_coefficient_voc']
                    
                    st.session_state.maxV = config_data['mppt_charger']['max_pv_voltage']
                    st.session_state.macA = config_data['mppt_charger']['max_charge_current_amps']
                    st.session_state.tcold = config_data['mppt_charger']['coldest_temperature_fahrenheit']
                    st.session_state.nominalpv12 = config_data['mppt_charger']['nominal_pv_power_12v_watts']
                    st.session_state.nominalpv24 = config_data['mppt_charger']['nominal_pv_power_24v_watts']
                    st.session_state.nominalpv48 = config_data['mppt_charger']['nominal_pv_power_48v_watts']
                    
                    st.session_state.battery_voltage = config_data['battery_system']['battery_bank_nominal_voltage']
                    
                    st.success("Configuration loaded successfully! (values will not show, but are uploaded! If you want to edit, you may click the calculations tab and then come back to this tab and uploaded values will appear)")
                    st.rerun()
                else:
                    st.error("File corrupted or invalid format")
        except (json.JSONDecodeError, KeyError, ValueError):
            st.error("File corrupted or invalid format")

with config_col3:
    if st.button("Reset to Defaults", use_container_width=True):
        # Clear all session state values
        st.session_state.ppp = 410.0
        st.session_state.voc = 37.41
        st.session_state.isc = 13.90
        st.session_state.vmp = 31.38
        st.session_state.imp = 13.07
        st.session_state.tempCoeff = -0.254
        
        st.session_state.maxV = 150.0
        st.session_state.macA = 60.0
        st.session_state.tcold = -10.0
        st.session_state.nominalpv12 = 860.0
        st.session_state.nominalpv24 = 1720.0
        st.session_state.nominalpv48 = 3440.0
        
        st.session_state.battery_voltage = 48.0
        
        st.success("✅ Reset to defaults")
        st.rerun()

st.divider()

# ============================================
# INPUT FIELDS (EXISTING CODE)
# ============================================

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.ppp = st.number_input("Power Per Panel (Watts)", min_value=0.0, value=st.session_state.ppp)
with col2:
    st.session_state.voc = st.number_input("Open Circuit Voltage (Voc) in Volts", min_value=0.0, value=st.session_state.voc)
with col3:
    st.session_state.isc = st.number_input("Short Circuit Current (Isc) in Amps", min_value=0.0, value=st.session_state.isc)

col4, col5, col6 = st.columns(3)
with col4:
    st.session_state.vmp = st.number_input("Voltage @ Max Power Point (Vmp) in Volts", min_value=0.0, value=st.session_state.vmp)
with col5:
    st.session_state.imp = st.number_input("Current @ Max Power Point (Imp) in Amps", min_value=0.0, value=st.session_state.imp)
with col6:
    st.session_state.tempCoeff = st.number_input(
        "Temperature Coefficient of Voc (%/°C)", 
        min_value=-1.0, 
        value=st.session_state.tempCoeff,
        step=0.001,
        help="Enter the percentage value (e.g., 0.324 for 0.324%/°C)",
        format="%.3f"
    )

st.divider()

st.header("Solar Charger Info")
st.subheader("Input Information From Your MPPT Charge Controller Datasheet")

col7, col8, col9 = st.columns(3)
with col7:
    st.session_state.maxV = st.number_input("Max PV Voltage", min_value=0.0, value=st.session_state.maxV)
with col8:
    st.session_state.macA = st.number_input("Max Charge Current (Amps)", min_value=0.0, value=st.session_state.macA)
with col9:
    st.session_state.tcold = st.number_input("Coldest Temperature That Your System May Encounter (°F)", min_value=-80.0, value=st.session_state.tcold)

col10, col11, col12 = st.columns(3)
with col10:
    st.session_state.nominalpv12 = st.number_input("Nominal PV Power in Watts for 12V", min_value=0.0, value=st.session_state.nominalpv12)
with col11:
    st.session_state.nominalpv24 = st.number_input("Nominal PV Power in Watts for 24V", min_value=0.0, value=st.session_state.nominalpv24)
with col12:
    st.session_state.nominalpv48 = st.number_input("Nominal PV Power in Watts for 48V", min_value=0.0, value=st.session_state.nominalpv48)

st.session_state.stc = 25 #this is in degrees C, but tcold is in F so we must convert at some point.

st.divider()

st.header("Battery System Info")
st.subheader("Input Information About Your Battery Bank")
st.session_state.battery_voltage = st.number_input("Battery Bank Nominal Voltage (12V, 24V or 48V)", min_value=0.0, value=st.session_state.battery_voltage)