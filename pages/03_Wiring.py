import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

st.header("Wiring Diagram & Fusing")

if 'selected_config' not in st.session_state:
    st.warning("Please select a configuration from the Calculations page first!")
else:
    config = st.session_state.selected_config
    
    st.subheader(f"Configuration: {config['config_str']}")
    
    # Display selected config info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Series Panels", config['series'])
    with col2:
        st.metric("Parallel Strings", config['parallel'])
    with col3:
        st.metric("Total Panels", config['total_panels'])
    with col4:
        st.metric("Config", config['config_str'])
    
    st.divider()
    
    # Calculate fusing
    st.subheader("Fusing Calculations")
    
    isc = st.session_state.isc
    voc_cold = st.session_state.get('voc_cold', st.session_state.voc)
    
    # PV String fuse (1.25x Isc per NEC)
    string_isc = isc * config['parallel']
    pv_fuse_calculated = string_isc * 1.25
    
    # Standard fuse ratings
    standard_fuses = [15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 125, 150]
    pv_fuse = next((f for f in standard_fuses if f >= pv_fuse_calculated), 150)
    
    # Disconnect/breaker on PV side (based on Voc)
    pv_disconnect_voltage = voc_cold * config['series']
    
    # Battery side fuse (1.25x battery current)
    battery_fuse_calculated = config['battery_current'] * 1.25
    battery_fuse = next((f for f in standard_fuses if f >= battery_fuse_calculated), 150)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("PV String Current (Isc)", f"{string_isc:.2f} A")
        st.metric("PV Fuse Rating", f"{pv_fuse} A")
        st.info(f"Calculated: {string_isc:.2f} A × 1.25 NEC factor")
    
    with col2:
        st.metric("PV Max Voltage", f"{pv_disconnect_voltage:.2f} V")
        st.metric("PV Disconnect Rating", f"{int(pv_disconnect_voltage) + 10} V minimum")
    
    with col3:
        st.metric("Battery Charging Current", f"{config['battery_current']:.2f} A")
        st.metric("Battery Fuse Rating", f"{battery_fuse} A")
        st.info(f"Calculated: {config['battery_current']:.2f} A × 1.25 NEC factor")
    
    st.divider()
    
    # ============================================
    # WIRE GAUGE CALCULATOR SECTION (NEW)
    # ============================================
    st.subheader("Wire Gauge Calculator")
    
    st.info("""
    📏 Enter the cable run distances for your system. The calculator will determine the minimum wire gauge needed 
    to keep voltage drop below recommended limits (3% for PV side, 2% for battery side).
    """)
    
    # Wire gauge reference table (AWG to resistance)
    wire_data = {
        'AWG': ['4', '6', '8', '10', '12', '2/0', '3/0', '4/0'],
        'Resistance (Ω/1000ft)': [0.49, 0.78, 1.24, 1.97, 3.14, 0.097, 0.077, 0.061],
        'Ampacity (DC, 60°C)': [85, 65, 50, 40, 25, 150, 175, 200]
    }
    wire_df = pd.DataFrame(wire_data)
    
    # Input section for cable runs
    st.write("**Enter your cable run distances:**")
    
    cable_col1, cable_col2 = st.columns(2)
    
    with cable_col1:
        pv_to_mppt_distance = st.number_input(
            "PV Array to MPPT Distance (feet)",
            min_value=0.0,
            value=20.0,
            step=1.0,
            help="One-way distance from solar panels to charge controller"
        )
    
    with cable_col2:
        mppt_to_battery_distance = st.number_input(
            "MPPT to Battery Distance (feet)",
            min_value=0.0,
            value=15.0,
            step=1.0,
            help="One-way distance from charge controller to battery bank"
        )
    
    
    # Wire gauge calculation function
    def calculate_wire_gauge(current, voltage, distance_one_way, max_voltage_drop_percent):
        """
        Calculate minimum wire gauge needed.
        
        Using Ohm's law and voltage drop formula:
        Voltage Drop = (2 × I × R × D) / 1000
        where:
        - I = current (amps)
        - R = resistance per 1000 feet (Ω/1000ft)
        - D = one-way distance (feet)
        - 2× accounts for round trip (out and back)
        """
        
        # Maximum allowable voltage drop in volts
        max_voltage_drop = (max_voltage_drop_percent / 100) * voltage
        
        # Calculate required resistance per 1000 feet
        # Rearranging: R = (VD × 1000) / (2 × I × D)
        required_resistance = (max_voltage_drop * 1000) / (2 * current * distance_one_way)
        
        # Wire specifications (AWG to Ω/1000ft)
        wire_specs = {
            '4': 0.49,
            '6': 0.78,
            '8': 1.24,
            '10': 1.97,
            '12': 3.14,
            '2/0': 0.097,
            '3/0': 0.077,
            '4/0': 0.061
        }
        
        # Find minimum gauge that meets requirement
        suitable_gauges = [g for g, r in wire_specs.items() if r <= required_resistance]
        
        if suitable_gauges:
            minimum_gauge = suitable_gauges[0]
            actual_resistance = wire_specs[minimum_gauge]
        else:
            minimum_gauge = '4/0'
            actual_resistance = wire_specs['4/0']
        
        # Calculate actual voltage drop with chosen wire
        actual_voltage_drop = (2 * current * actual_resistance * distance_one_way) / 1000
        actual_voltage_drop_percent = (actual_voltage_drop / voltage) * 100
        
        return {
            'gauge': minimum_gauge,
            'required_resistance': required_resistance,
            'actual_resistance': actual_resistance,
            'voltage_drop': actual_voltage_drop,
            'voltage_drop_percent': actual_voltage_drop_percent,
            'meets_spec': actual_voltage_drop_percent <= max_voltage_drop_percent
        }
    
    # Calculate for PV side
    if st.button("Calculate Wire Gauges"):
        pv_result = calculate_wire_gauge(
            current=config['panel_current'],
            voltage=config['panel_voltage'],
            distance_one_way=pv_to_mppt_distance,
            max_voltage_drop_percent=3.0  # NEC standard: 3% for sub-circuits
        )
        
        battery_result = calculate_wire_gauge(
            current=config['battery_current'],
            voltage=config['battery_voltage'],
            distance_one_way=mppt_to_battery_distance,
            max_voltage_drop_percent=2.0  # More stringent for battery side
        )
        
        # Store in session state
        st.session_state.pv_wire_result = pv_result
        st.session_state.battery_wire_result = battery_result
    
    # Display results if available
    if 'pv_wire_result' in st.session_state and 'battery_wire_result' in st.session_state:
        pv_result = st.session_state.pv_wire_result
        battery_result = st.session_state.battery_wire_result
        
        st.subheader("Wire Gauge Results")
        
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.write("**PV Array to MPPT**")
            st.metric("Minimum Wire Gauge", f"AWG {pv_result['gauge']}", 
                     delta=f"VD: {pv_result['voltage_drop_percent']:.2f}%")
            
            if pv_result['meets_spec']:
                st.success(f"✓ Meets 3% limit ({pv_result['voltage_drop']:.2f}V drop)")
            else:
                st.error(f"✗ Exceeds 3% limit ({pv_result['voltage_drop']:.2f}V drop)")
            
            with st.expander("PV Calculation Details"):
                st.write(f"**Current:** {config['panel_current']:.2f} A")
                st.write(f"**Voltage:** {config['panel_voltage']:.2f} V")
                st.write(f"**Distance:** {pv_to_mppt_distance} ft (one-way)")
                st.write(f"**Max Voltage Drop Allowed (3%):** {(0.03 * config['panel_voltage']):.2f} V")
                st.write(f"**Required Resistance:** {pv_result['required_resistance']:.4f} Ω/1000ft")
                st.write(f"**Selected Wire (AWG {pv_result['gauge']}):** {pv_result['actual_resistance']:.4f} Ω/1000ft")
                st.latex(r"V_{drop} = \frac{2 \times I \times R \times D}{1000}")
                st.write(f"V_drop = (2 × {config['panel_current']:.2f} × {pv_result['actual_resistance']:.4f} × {pv_to_mppt_distance}) / 1000 = **{pv_result['voltage_drop']:.2f}V**")
        
        with result_col2:
            st.write("**MPPT to Battery**")
            st.metric("Minimum Wire Gauge", f"AWG {battery_result['gauge']}", 
                     delta=f"VD: {battery_result['voltage_drop_percent']:.2f}%")
            
            if battery_result['meets_spec']:
                st.success(f"✓ Meets 2% limit ({battery_result['voltage_drop']:.2f}V drop)")
            else:
                st.error(f"✗ Exceeds 2% limit ({battery_result['voltage_drop']:.2f}V drop)")
            
            with st.expander("Battery Calculation Details"):
                st.write(f"**Current:** {config['battery_current']:.2f} A")
                st.write(f"**Voltage:** {config['battery_voltage']:.2f} V")
                st.write(f"**Distance:** {mppt_to_battery_distance} ft (one-way)")
                st.write(f"**Max Voltage Drop Allowed (2%):** {(0.02 * config['battery_voltage']):.2f} V")
                st.write(f"**Required Resistance:** {battery_result['required_resistance']:.4f} Ω/1000ft")
                st.write(f"**Selected Wire (AWG {battery_result['gauge']}):** {battery_result['actual_resistance']:.4f} Ω/1000ft")
                st.latex(r"V_{drop} = \frac{2 \times I \times R \times D}{1000}")
                st.write(f"V_drop = (2 × {config['battery_current']:.2f} × {battery_result['actual_resistance']:.4f} × {mppt_to_battery_distance}) / 1000 = **{battery_result['voltage_drop']:.2f}V**")
        
        st.divider()
        
        # Wire gauge reference table
        st.subheader("Wire Gauge Reference")
        st.write("*Common DC wire gauges and their specifications (copper wire at 60°C):*")
        st.dataframe(wire_df, use_container_width=True, hide_index=True)
        
        st.info("""
        **Notes:**
        - All wire should be rated for at least the **Ampacity** listed for your circuit
        - Use 2× the calculated ampacity for fused circuits (safety margin)
        - Use **stranded copper wire** in outdoor installations for better flexibility and corrosion resistance
        - All conduit and terminals must be rated for the voltage and current of your system
        - For runs >100ft, consider increasing wire gauge further to account for temperature effects
        """)
        
        st.divider()
    
    # Generate wiring diagram
    st.subheader("Wiring Diagram")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    color_pv = '#FFD700'
    color_mppt = '#87CEEB'
    color_battery = '#FF6B6B'
    color_wire = '#333333'
    
    # Helper function to draw boxes
    def draw_box(ax, x, y, width, height, label, color, fontsize=10):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                            boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=fontsize, weight='bold')
    
    # Helper function to draw connection labels
    def draw_label(ax, x, y, text, fontsize=9):
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Colors for wiring
    color_positive = '#FF0000'  # Red for positive
    color_negative = '#000000'   # Black for negative
    color_ground = '#FFD700'   # Gold for ground

    ####################################################

    # Solar Panels (left side)
    panel_y_start = 8.5
    panel_spacing = 1.5
    panel_x_spacing = 2

    # Draw all panels
    for p in range(config['parallel']):
        for i in range(config['series']):
            y_pos = panel_y_start - (i * panel_spacing)
            x_pos = 0.8 + (p * panel_x_spacing)
            draw_box(ax, x_pos, y_pos, 0.8, 0.6, f"PV", color_pv, fontsize=9)
            # Add terminal labels
            ax.text(x_pos + 0.7, y_pos + 0.5, '+', ha='center', va='center', fontsize=12, weight='bold', color='red',
                bbox=dict(boxstyle='circle', facecolor='white', edgecolor='red', linewidth=1))
            ax.text(x_pos + 0.7, y_pos - 0.5, '−', ha='center', va='center', fontsize=12, weight='bold', color='black',
                bbox=dict(boxstyle='circle', facecolor='white', edgecolor='black', linewidth=1))

    # Draw series connections (within each string - + to −)
    for p in range(config['parallel']):
        x_pos = 0.8 + (p * panel_x_spacing)
        for i in range(config['series'] - 1):
            y_start = panel_y_start - (i * panel_spacing)
            y_end = panel_y_start - ((i + 1) * panel_spacing)
            
            ax.plot([x_pos + 0.8, x_pos + 1.3], [y_start + 0.5, y_start + 0.5], 
                    color=color_positive, linewidth=2.5)
            ax.plot([x_pos + 1.3, x_pos + 1.3], [y_start + 0.5, y_end - 0.5], 
                    color=color_positive, linewidth=2.5)
            ax.plot([x_pos + 1.3, x_pos + 0.8], [y_end - 0.5, y_end - 0.5], 
                    color=color_positive, linewidth=2.5)

    # Draw parallel connections (+ to + above, − to − below)
    for i in range(config['series']):
        y_pos = panel_y_start - (i * panel_spacing)
        
        for p in range(config['parallel'] - 1):
            x_start = 0.8 + (p * panel_x_spacing)
            x_end = 0.8 + ((p + 1) * panel_x_spacing)
            
            # Red: + to + (above)
            ax.plot([x_start + 0.7, x_start + 0.7, x_end + 0.7, x_end + 0.7], 
                    [y_pos + 0.5, y_pos + 1.0, y_pos + 1.0, y_pos + 0.5], 
                    color=color_positive, linewidth=2.5)
            
            # Black: − to − (below)
            ax.plot([x_start + 0.7, x_start + 0.7, x_end + 0.7, x_end + 0.7], 
                    [y_pos - 0.5, y_pos - 1.0, y_pos - 1.0, y_pos - 0.5], 
                    color=color_negative, linewidth=2.5)

    # Output from PV array (from the last string)
    output_x = 0.8 + ((config['parallel'] - 1) * panel_x_spacing) + 0.7
    output_y_pos = panel_y_start  # Top panel +
    output_y_neg = panel_y_start - ((config['series'] - 1) * panel_spacing)  # Bottom panel −

    # Route from array to MPPT
    ax.plot([output_x, 5.5], [output_y_pos, output_y_pos], color=color_positive, linewidth=2.5)
    ax.plot([5.5, 6.25], [output_y_pos, 6.8], color=color_positive, linewidth=2.5)

    ax.plot([output_x, 5.5], [output_y_neg, output_y_neg], color=color_negative, linewidth=2.5)
    ax.plot([5.5, 6.25], [output_y_neg, 6.2], color=color_negative, linewidth=2.5)

    # Add wire gauge labels to diagram (if available)
    if 'pv_wire_result' in st.session_state:
        pv_result = st.session_state.pv_wire_result
        draw_label(ax, 5.5, 7.2, f"AWG {pv_result['gauge']}\n{pv_to_mppt_distance}ft", fontsize=8)

    # MPPT Charge Controller
    draw_box(ax, 7.5, 6.5, 1.5, 1, "MPPT\nController", color_mppt, fontsize=10)
    draw_label(ax, 7.5, 5.1, f"In:{config['panel_voltage']:.0f}V@{config['panel_current']:.1f}A\nOut:{config['battery_voltage']:.0f}V@{config['battery_current']:.1f}A", fontsize=7)

    # From MPPT to Battery
    ax.plot([8.75, 11.5], [6.8, 6.8], color=color_positive, linewidth=2.5)
    ax.plot([8.75, 11.5], [6.2, 6.2], color=color_negative, linewidth=2.5)

    # Add wire gauge labels to diagram (if available)
    if 'battery_wire_result' in st.session_state:
        battery_result = st.session_state.battery_wire_result
        draw_label(ax, 10, 7.2, f"AWG {battery_result['gauge']}\n{mppt_to_battery_distance}ft", fontsize=8)

    # Battery
    draw_box(ax, 12.5, 6.5, 1.2, 0.8, f"Battery\n{config['battery_voltage']:.0f}V", color_battery, fontsize=10)
    draw_label(ax, 12.5, 5.2, f"Charge:{config['battery_current']:.1f}A\nPower:{config['panel_power']:.0f}W", fontsize=7)

    # Ground connections
    ax.plot([7.5, 7.5], [7.0, 7.8], color=color_ground, linewidth=1.5, linestyle='--')
    ax.plot([12.5, 12.5], [6.0, 5.0], color=color_ground, linewidth=1.5, linestyle='--')

    # Add title
    ax.text(7, 9.7, f"PV System Wiring Diagram - {config['config_str']}", 
        ha='center', fontsize=14, weight='bold')

    # Add legend and config info
    ax.text(0.2, 0.5, "Red = Positive (+)  |  Black = Negative (−)  |  Gold Dashed = Ground", 
            fontsize=8, style='italic', weight='bold')
    ax.text(0.2, -0.1, f"Config: {config['series']}S × {config['parallel']}P  =  {config['series']} panels/string × {config['parallel']} parallel strings", 
            fontsize=8, weight='bold')

    ####################################################

    plt.tight_layout()
    st.pyplot(fig)
    
    st.divider()
    
    st.subheader("Component Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.write("**PV Array**")
        st.write(f"- {config['series']} panels in series")
        st.write(f"- {config['parallel']} parallel string(s)")
        st.write(f"- Output: {config['panel_voltage']:.2f}V @ {config['panel_current']:.2f}A")
        st.write(f"- Total Power: {config['panel_power']:.0f}W")
    
    with summary_col2:
        st.write("**Protection & Control**")
        st.write(f"- PV Fuse: {pv_fuse}A DC")
        st.write(f"- PV Disconnect: ≥{int(pv_disconnect_voltage) + 10}V rated")
        st.write(f"- MPPT: {st.session_state.maxV}V max input")
        st.write(f"- MPPT: {st.session_state.macA}A max output")
    
    with summary_col3:
        st.write("**Battery System**")
        st.write(f"- Nominal Voltage: {config['battery_voltage']:.0f}V")
        st.write(f"- Charging Current: {config['battery_current']:.2f}A")
        st.write(f"- Battery Fuse: {battery_fuse}A DC")
        st.write(f"- Max Power: {config['panel_power']:.0f}W")