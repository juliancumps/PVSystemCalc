import streamlit as st

st.header("Solar Panel Info")
st.subheader("Input Information From Your Solar Panel Datasheet")


col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.ppp = st.number_input("Power Per Panel (Watts)", min_value=0.0, value=410.00)
with col2:
    st.session_state.voc = st.number_input("Open Circuit Voltage (Voc) in Volts", min_value=0.0, value=37.41)
with col3:
    st.session_state.isc = st.number_input("Short Circuit Current (Isc) in Amps", min_value=0.0, value=13.90)

col4, col5, col6 = st.columns(3)
with col4:
    st.session_state.vmp = st.number_input("Voltage @ Max Power Point (Vmp) in Volts", min_value=0.0, value=31.38)
with col5:
    st.session_state.imp = st.number_input("Current @ Max Power Point (Imp) in Amps)", min_value=0.0, value=13.07)
with col6:
    st.session_state.tempCoeff = st.number_input(
        "Temperature Coefficient of Voc (%/°C)", 
        min_value=-1.0, 
        value=-0.254,
        step=0.001,
        help="Enter the percentage value (e.g., 0.324 for 0.324%/°C)",
        format="%.3f"
    )

st.divider()

st.header("Solar Charger Info")
st.subheader("Input Information From Your MPPT Charge Controller Datasheet")

col7, col8, col9 = st.columns(3)
with col7:
    st.session_state.maxV = st.number_input("Max PV Voltage", min_value=0.0, value=150.0)
with col8:
    st.session_state.macA = st.number_input("Max Charge Current (Amps)", min_value=0.0, value=60.0)
with col9:
    st.session_state.tcold = st.number_input("Coldest Temperature That Your System May Encounter (°F)", min_value=-80.0, value=-10.0)

col10, col11, col12 = st.columns(3)
with col10:
    st.session_state.nominalpv12 = st.number_input("Nominal PV Power in Watts for 12V", min_value=0.0, value=860.0)
with col11:
    st.session_state.nominalpv24 = st.number_input("Nominal PV Power in Watts for 24V", min_value=0.0, value=1720.0)
with col12:
    st.session_state.nominalpv48 = st.number_input("Nominal PV Power in Watts for 48V", min_value=0.0, value=3440.0)

st.session_state.stc = 25 #this is in degrees C, but tcold is in F so we must convert at some point.

st.divider()

st.header("Battery System Info")
st.subheader("Input Information About Your Battery Bank")
st.session_state.battery_voltage = st.number_input("Battery Bank Nominal Voltage (12V, 24V or 48V)", min_value=0.0, value=48.0)
