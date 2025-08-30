# Units

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://units-liborbenes-us.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues/LiborBenes-US/Units.svg)](https://github.com/LiborBenes-US/Units/issues)

## 📖 Description
**Units** is a comprehensive unit conversion tool built with [Streamlit](https://streamlit.io/).  
It supports:
- U.S. customary units (including legacy/deprecated ones used in older documents)
- Metric & SI units
- Temperature conversions (Celsius, Fahrenheit, Kelvin)
- Length, distance, area, volume, weight, and more
- Number systems (binary, octal, decimal, hexadecimal)
- Encoders/decoders (Base64, URL, HTML, etc.)
- Hashing (MD5, SHA-1, SHA-256, SHA-512)

## 🚀 Features
- **High precision inputs**: You can enter as many decimal places as needed. This allows for exact values in scientific or mathematical work (e.g., precise Pi usage).
- **Session history**: All conversions in the current session are stored. You can review them while the app is open.
- **Download history**: Export your session’s conversions as a CSV before closing the page.  
  *(No information is stored after you close the browser tab — your data is never saved on the server.)*
- **Safety**: All inputs are sanitized to prevent malicious use. No data is transmitted outside the app, except when you choose to visit GitHub for feedback.

## 📷 Screenshot
(*To be added after deployment*)

## 🛠️ Installation & Local Use
Clone the repository and install dependencies:

```bash
git clone https://github.com/LiborBenes-US/Units.git
cd Units
pip install -r requirements.txt
streamlit run units.py
