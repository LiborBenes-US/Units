# Units — Universal Converter ⚖️

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://units1.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE.txt)
[![GitHub Issues](https://img.shields.io/github/issues/LiborBenes-US/Units.svg)](https://github.com/LiborBenes-US/Units/issues)

**Converter: U.S. & Metric Units**

[Units](https://units1.streamlit.app) is a comprehensive, ad-free unit conversion tool built with [Streamlit](https://streamlit.io) and `pint`. Deployed at [units1.streamlit.app](https://units1.streamlit.app).  
It supports a wide range of conversions, including:

- 📏 **Length** (metric, imperial, U.S. survey, nautical, etc.)
- 🏞️ **Area** (square meters, acres, hectares, etc.)
- 💧 **Volume** (liters, gallons, barrels, cups, etc.)
- ⚖️ **Mass & Weight** (kg, lb, tons, centners, etc.)
- 🌡️ **Temperature** (Celsius, Fahrenheit, Kelvin)
- 🚀 **Speed** (km/h, mph, knots, etc.)
- 🌬️ **Pressure** (pascal, bar, psi, etc.)
- ⚡ **Energy & Power** (joule, calorie, watt, etc.)
- ⛽ **Fuel Economy** (liter/100 km, mile/gallon, etc.)
- 🖥️ **Digital Storage** (bytes, bits, prefixes, etc.)
- 📐 **Angle** (degree, radian, grad)
- 🔢 **Number Bases** (bin/oct/dec/hex)
- 🔤 **ASCII/Unicode** (char ↔ hex/bin/oct/dec)
- 🔐 **Encodings & Hashes** (Base64, URL, MD5, SHA-1, SHA-256, SHA-512)

**[Open Converter 🚀](https://units1.streamlit.app)** | **[Suggest a Unit 📝](https://github.com/LiborBenes-US/Units/issues)**

---

## ✨ Features
- **Categories**: Length, Area, Volume, Mass, Temperature, Speed, Pressure, Energy & Power, Fuel Economy, Digital Storage, Angle.
- **Precision**: Supports high-precision Decimal input; output precision is adjustable via a slider (3–60 decimal places).
- **Unit Definitions**: Aligned with NIST standards (Handbook 44, SP 811) for maximum accuracy. Note that results may differ slightly from some online calculators due to rounding or differing standards (e.g., `1 gallon_us = 3.785411784 liter` per NIST vs. `~3.785 liter` in some tools).
- **Additional Tools**: Number base conversions (bin/oct/dec/hex), ASCII/Unicode code points, encodings (Base64, URL), and cryptographic hashes (MD5, SHA-1, SHA-256, SHA-512).
- **Session History**: Stored in-memory for the current browser tab; downloadable as JSON or CSV.
- **Unit Suggestions**: Submit new unit requests via [GitHub Issues](https://github.com/LiborBenes-US/Units/issues) (no data is sent from the app).
- **Safe Input**: Dropdown-based unit selection to prevent typos.
- **Expandable**: Easily extendable for future conversions.

---

## 🚀 Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/LiborBenes-US/Units.git
cd Units
pip install -r requirements.txt
streamlit run units.py
