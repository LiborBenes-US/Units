# Units

**Converter: U.S. & Metric Units**

Units is a comprehensive unit conversion app built with [Streamlit](https://streamlit.io).  
It supports a wide range of conversions including:

- 📏 Length (metric, imperial, U.S. survey, nautical, etc.)
- ⚖️ Mass & Weight (kg, lb, tons, centners, etc.)
- 💧 Volume (liters, gallons, barrels, cups, etc.)
- ⏱️ Time
- 🌡️ Temperature
- 🖥️ IT & Digital (bytes, bits, prefixes, bin/hex/oct/dec, hashes, encoding/decoding)
- 🔤 ASCII Table (char ↔ hex/bin/oct/dec)

### ✨ Features
- Arbitrary precision decimal input (using Python `Decimal`).
- Session-based history of conversions.
- Download your session history before closing the app.
- Safe, dropdown-based unit selection to prevent typos.
- Expandable for future conversions.

### 🚀 Run Locally
Clone the repository and install dependencies:
```bash
git clone https://github.com/LiborBenes-US/Units.git
cd Units
pip install -r requirements.txt
streamlit run units.py
