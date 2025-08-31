# Units — Universal Converter

A comprehensive, ad-free unit conversion tool built with Streamlit and `pint`, supporting a wide range of units across multiple categories. Deployed at [units1.streamlit.app](https://units1.streamlit.app).

## Features
- **Categories**: Length, Area, Volume, Mass, Temperature, Speed, Pressure, Energy & Power, Fuel Economy, Digital Storage, Angle.
- **Precision**: Supports high-precision Decimal input; output precision is adjustable via a slider (3–60 decimal places).
- **Unit Definitions**: Aligned with NIST standards (Handbook 44, SP 811) for maximum accuracy. Note that results may differ slightly from some online calculators due to rounding or differing standards (e.g., `1 gallon_us = 3.785411784 liter` per NIST vs. ~3.785 liter in some tools).
- **Additional Tools**: Number base conversions (bin/oct/dec/hex), ASCII/Unicode code points, encodings (Base64, URL), and cryptographic hashes (MD5, SHA-1, SHA-256, SHA-512).
- **Session History**: Stored in-memory for the current browser tab; downloadable as JSON or CSV.
- **Unit Suggestions**: Submit new unit requests via GitHub Issues (no data is sent from the app).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/LiborBenes-US/Units.git
   cd Units
