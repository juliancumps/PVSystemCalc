# PV System Calculator

A practical tool for designing safe solar photovoltaic systems with MPPT charge controllers. The calculator determines safe panel configurations, calculates proper fusing, and sizes wiring based on actual run distances.

## Overview

This application guides you through four key steps in designing a PV system:

1. **Inputs** - Enter solar panel and charge controller specifications
2. **Calculations** - Find safe panel configurations that respect voltage and current limits
3. **Wiring** - View the system diagram and calculate proper wire gauges
4. **Configuration Management** - Save and load your configurations as JSON files

## Features

### Configuration Management

Save your system inputs as a JSON file for reuse across devices or to share with others. Load previously saved configurations to quickly set up similar systems.

- Generate and download JSON configurations
- Upload configurations to auto-populate all fields
- Reset all values to defaults with a single button
- Full validation of uploaded files

### Safe Configuration Finder

The calculator tests all possible series and parallel combinations against your charge controller limits:

- Maximum PV voltage rating
- Maximum charge current rating
- Power rating limits for different system voltages

Results show which configurations are safe and which exceed limits, sorted by total panel count.

### Wire Gauge Calculator

Calculate minimum wire gauges based on actual cable run distances:

- PV array to MPPT distance
- MPPT to battery distance
- Voltage drop calculations (3% limit for PV side, 2% for battery side)
- Resistance and ampacity reference table
- Wire gauge labels on the system diagram

### Wiring Diagram

Visual representation of your selected configuration including:

- Panel series/parallel arrangement
- Component connections (MPPT, battery)
- Wire gauge and distances labeled
- Component ratings summary

### Fusing Calculations

Automatic calculation of required fuse ratings:

- PV string fuses (1.25x Isc per NEC)
- Battery side fuses (1.25x charging current)
- PV disconnect voltage rating

## Requirements

- Python 3.11+
- Streamlit 1.54.0 or later
- matplotlib
- pandas
- numpy

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

1. Start on the Inputs page and enter your solar panel specifications from the datasheet
2. Add your MPPT charge controller specifications
3. Enter your battery bank nominal voltage
4. Navigate to Calculations and run each calculation in order
5. Select a safe configuration
6. Go to Wiring to view the diagram and wire gauge requirements
7. Save your configuration as JSON for future reference

## Technical Notes

The calculator assumes:

- Copper wiring (not aluminum)
- Temperature coefficient provided in %/°C format
- Coldest temperature in Fahrenheit
- STC (Standard Test Conditions) at 25°C

Voltage drop limits follow industry standards: 3% maximum for PV circuits, 2% for battery circuits. For outdoor installations or future expansion, consider using one wire gauge larger than the calculated minimum.

## Limitations

This tool is designed for MPPT charge controller systems. It does not account for:

- Battery discharge loads
- System efficiency losses beyond basic fusing
- Temperature derating of components beyond panel cold voltage
- Complex multi-MPPT configurations

Always verify calculations against your specific equipment datasheets and local electrical codes before installation.

## License

MIT License - See LICENSE file for details
