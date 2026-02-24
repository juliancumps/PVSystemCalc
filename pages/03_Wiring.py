import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

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
        st.info(f"Calculated: {pv_fuse_calculated:.2f} A × 1.25 NEC factor")
    
    with col2:
        st.metric("PV Max Voltage", f"{pv_disconnect_voltage:.2f} V")
        st.metric("PV Disconnect Rating", f"{int(pv_disconnect_voltage) + 10} V minimum")
    
    with col3:
        st.metric("Battery Charging Current", f"{config['battery_current']:.2f} A")
        st.metric("Battery Fuse Rating", f"{battery_fuse} A")
        st.info(f"Calculated: {config['battery_current']:.2f} A × 1.25 NEC factor")
    
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
    
    # Solar Panels (left side)
    panel_y_start = 8
    panel_spacing = 1.2
    
    for i in range(config['series']):
        y_pos = panel_y_start - (i * panel_spacing)
        draw_box(ax, 1.5, y_pos, 0.8, 0.6, f"PV{i+1}", color_pv, fontsize=8)
    
    # Draw parallel strings if needed
    if config['parallel'] > 1:
        for p in range(1, config['parallel']):
            for i in range(config['series']):
                y_pos = panel_y_start - (i * panel_spacing)
                draw_box(ax, 1.5 + (p * 1.2), y_pos, 0.8, 0.6, f"PV{i+1}", color_pv, fontsize=8)
    
    # PV combiner box with fuse
    draw_box(ax, 4, 6.5, 1.2, 0.8, f"PV Fuse\n{pv_fuse}A", '#FFE4B5', fontsize=9)
    draw_label(ax, 4, 7.8, f"Isc: {string_isc:.1f}A\nVoc: {pv_disconnect_voltage:.1f}V", fontsize=8)
    
    # MPPT Charge Controller (center)
    draw_box(ax, 7, 6.5, 1.5, 1, "MPPT\nController", color_mppt, fontsize=10)
    draw_label(ax, 7, 5.2, f"Input: {config['panel_voltage']:.1f}V @ {config['panel_current']:.1f}A\nPower: {config['panel_power']:.0f}W", fontsize=8)
    
    # Battery Fuse
    draw_box(ax, 10, 6.5, 1.2, 0.8, f"Batt Fuse\n{battery_fuse}A", '#FFE4B5', fontsize=9)
    draw_label(ax, 10, 7.8, f"I: {config['battery_current']:.1f}A\nV: {config['battery_voltage']:.0f}V", fontsize=8)
    
    # Battery (right side)
    draw_box(ax, 12.5, 6.5, 1.2, 0.8, f"Battery\n{config['battery_voltage']:.0f}V", color_battery, fontsize=10)
    draw_label(ax, 12.5, 5.2, f"Output: {config['battery_current']:.1f}A\nPower: {config['panel_power']:.0f}W", fontsize=8)
    
    # Draw wiring connections
    # PV to combiner
    ax.plot([2.5, 3.4], [6.5, 6.5], color=color_wire, linewidth=2)
    draw_label(ax, 2.9, 6.8, f"{config['panel_voltage']:.0f}V", fontsize=8)
    
    # Combiner to MPPT
    ax.plot([4.6, 6.25], [6.5, 6.5], color=color_wire, linewidth=2)
    
    # MPPT to Battery Fuse
    ax.plot([7.75, 9.4], [6.5, 6.5], color=color_wire, linewidth=2)
    draw_label(ax, 8.6, 6.8, f"{config['battery_voltage']:.0f}V\n{config['battery_current']:.1f}A", fontsize=8)
    
    # Fuse to Battery
    ax.plot([10.6, 11.9], [6.5, 6.5], color=color_wire, linewidth=2)
    
    # Ground connections
    ax.plot([1.5, 1.5], [7.8, 8.5], color=color_wire, linewidth=1.5, linestyle='--')
    ax.plot([7, 7], [7, 7.5], color=color_wire, linewidth=1.5, linestyle='--')
    ax.plot([12.5, 12.5], [5.8, 5.2], color=color_wire, linewidth=1.5, linestyle='--')
    
    # Add title and legend
    ax.text(7, 9.5, f"PV System Wiring Diagram - {config['config_str']}", 
           ha='center', fontsize=14, weight='bold')
    
    ax.text(0.5, 0.8, f"Panel Config: {config['series']}S × {config['parallel']}P = {config['total_panels']} panels", fontsize=9)
    ax.text(0.5, 0.2, "Dashed lines = Ground connections | All fuses rated for DC solar applications", fontsize=8, style='italic')
    
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