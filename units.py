# units.py
# Units — Universal Converter (Streamlit)
# Save as units.py and run with: streamlit run units.py

import streamlit as st
from decimal import Decimal, getcontext, InvalidOperation
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from mpmath import mp
import io, json, csv, hashlib, base64, binascii, urllib.parse, html
import pandas as pd

# ----------------------------
# CONFIG
# ----------------------------
getcontext().prec = 200

GITHUB_OWNER = "LiborBenes-US"
GITHUB_REPO = "Units"
ISSUE_TITLE = urllib.parse.quote("Unit suggestion:")
ISSUE_BODY = urllib.parse.quote(
    "Please describe the unit you'd like added (name, exact definition/ratio to SI unit, and source/reference).\n\nExample:\n- name: 'tablespoon_au'\n- definition: 20 mL\n- note: 'Australian tablespoon'"
)
GITHUB_ISSUE_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/new?title={ISSUE_TITLE}&body={ISSUE_BODY}"

st.set_page_config(page_title="Units — Universal Converter", layout="wide", page_icon="⚖️")
st.title("Units — Universal Converter ⚖️")
st.markdown("**Converter: U.S. & Metric Units** — ad-free, comprehensive, and safe. Session history can be downloaded (only stored for current tab/session).")

# ----------------------------
# UNIT REGISTRY (pint) + extras
# ----------------------------
ureg = UnitRegistry()
Q_ = ureg.Quantity

EXTRA_DEFS = """
# Length (NIST SP 811, Handbook 44)
nautical_mile = 1852 * meter = nmi
statute_mile = 1609.344 * meter
mile_us_survey = 1609.347218694 * meter
foot_us_survey = 0.3048006096 * meter
inch = 0.0254 * meter
yard = 0.9144 * meter

# Area (NIST SP 811)
acre_intl = 4046.8564224 * meter**2
acre_us_survey = 4046.872609874 * meter**2

# Volume (NIST SP 811, Handbook 44)
gallon_us = 3.785411784 * liter
fluid_ounce_us = 0.0295735295625 * liter
cup_us = 0.2365882365 * liter
pint_us = 0.473176473 * liter
quart_us = 0.946352946 * liter
fluid_ounce_imp = 0.0284130625 * liter
pint_imp = 0.56826125 * liter
quart_imp = 1.1365225 * liter
gallon_imp = 4.54609 * liter
teaspoon_us = 0.00492892159375 * liter
tablespoon_us = 0.01478676478125 * liter
tablespoon_metric = 0.015 * liter
tablespoon_au = 0.02 * liter
barrel_oil_us = 158.987294928 * liter
barrel_beer_us = 117.347765304 * liter
barrel_beer_uk = 163.65924 * liter

# Mass (NIST SP 811)
pound = 0.45359237 * kilogram
ton_short = 907.18474 * kilogram
ton_long = 1016.0469088 * kilogram
tonne = 1000 * kilogram = t
quintal = 100 * kilogram = q
ounce = 0.028349523125 * kilogram
stone = 6.35029318 * kilogram

# Speed (derived from NIST length/time)
knot = 0.514444444 * meter/second
mile_per_hour = 0.44704 * meter/second

# Pressure (NIST SP 811)
bar = 100000 * pascal
millibar = 100 * pascal = mbar
atmosphere = 101325 * pascal
mmHg = 133.322387415 * pascal
psi = 6894.757293168 * pascal

# Energy & Power (NIST SP 811)
calorie = 4.184 * joule
kcal = 4184 * joule
BTU = 1055.05585262 * joule
watt_hour = 3600 * joule
kilowatt_hour = 3600000 * joule

# Fuel Economy (derived from NIST length/volume)
mile_per_gallon_us = statute_mile / gallon_us = mpg_us
mile_per_gallon_imp = statute_mile / gallon_imp = mpg_imp
# Use the conversion factor: 1 L/100km = 235.2145833 / mpg
liter_per_100_kilometer = (235.2145833 / mile_per_gallon_us) = L/100km

# Digital Storage (IEC/SI standards)
byte = [information]
kB = 1000 * byte
MB = 1000000 * byte
GB = 1000000000 * byte
TB = 1000000000000 * byte
PB = 1000000000000000 * byte
KiB = 1024 * byte
MiB = 1048576 * byte
GiB = 1073741824 * byte
TiB = 1099511627776 * byte
PiB = 1125899906842624 * byte

# Angle (NIST SP 811)
degree = 0.0174532925199433 * radian
grad = 0.015707963267949 * radian
"""

for line in EXTRA_DEFS.splitlines():
    line = line.strip()
    if line and not line.startswith('#'):
        ureg.define(line)

# Debug conversions
def debug_conversion(value, from_unit, to_unit):
    try:
        q_from = quantity_from_decimal(Decimal(str(value)), from_unit)
        if q_from is None:
            print(f"Failed to create quantity for {value} {from_unit}")
            return
        q_to = q_from.to(to_unit)
        print(f"{value} {from_unit} = {q_to.magnitude} {to_unit}")
    except Exception as e:
        print(f"Error converting {value} {from_unit} to {to_unit}: {e}")

debug_tests = [
    (2.718, "acre_intl", "hectare"),
    (3.14159, "gallon_us", "liter"),
    (1, "barrel_oil_us", "gallon_imp"),
    (123.456, "pound", "kilogram"),
    (0.9876, "ton_short", "tonne"),
    (37.5, "degC", "degF"),
    (88.6, "kilometer/hour", "mile_per_hour"),
    (1013.25, "millibar", "pascal"),
    (5000, "joule", "calorie"),
    (8.5, "liter_per_100_kilometer", "mile_per_gallon_us"),
    (1024, "MiB", "MB"),
    (180, "degree", "radian"),
    (1.23456789e-10, "meter", "nanometer"),
    (1234567890123, "byte", "TB"),
    (-40, "degF", "degC"),
]
for value, from_unit, to_unit in debug_tests:
    debug_conversion(value, from_unit, to_unit)

# ----------------------------
# UNIT CATEGORIES and LISTS
# ----------------------------
CATEGORIES = {
    "Length": [
        "nanometer", "micrometer", "millimeter", "centimeter", "decimeter", "meter", "kilometer",
        "inch", "foot", "foot_us_survey", "yard", "statute_mile", "mile_us_survey", "nautical_mile"
    ],
    "Area": [
        "millimeter**2", "centimeter**2", "meter**2", "hectare", "acre_intl", "acre_us_survey", "kilometer**2",
        "square_inch", "square_foot", "square_yard", "square_mile"
    ],
    "Volume": [
        "milliliter", "centiliter", "deciliter", "liter", "hectoliter", "meter**3",
        "teaspoon_us", "tablespoon_us", "tablespoon_metric", "tablespoon_au",
        "fluid_ounce_us", "cup_us", "pint_us", "quart_us", "gallon_us",
        "fluid_ounce_imp", "pint_imp", "quart_imp", "gallon_imp",
        "barrel_oil_us", "barrel_beer_us", "barrel_beer_uk"
    ],
    "Mass": [
        "milligram", "gram", "kilogram", "quintal", "tonne", "ounce", "pound", "stone", "ton_short", "ton_long"
    ],
    "Temperature": ["degC", "degF", "kelvin"],
    "Speed": ["meter/second", "kilometer/hour", "mile_per_hour", "knot"],
    "Pressure": ["pascal", "kilopascal", "bar", "millibar", "atmosphere", "mmHg", "psi"],
    "Energy & Power": ["joule", "kilojoule", "watt_hour", "kilowatt_hour", "calorie", "kcal", "BTU", "watt"],
    "Fuel economy": ["liter_per_100_kilometer", "mile_per_gallon_us", "mile_per_gallon_imp"],
    "Digital storage": ["bit", "byte", "kB", "MB", "GB", "TB", "PB", "KiB", "MiB", "GiB", "TiB", "PiB"],
    "Angle": ["degree", "radian", "grad"]
}

def pretty_unit_label(u):
    lab = (u.replace("**2", "²")
           .replace("**3", "³")
           .replace("_", " ")
           .replace("*", "·")
           .replace("liter_per_100_kilometer", "liter/100 km")
           .replace("mile_per_gallon_us", "mile/gallon (US)")
           .replace("mile_per_gallon_imp", "mile/gallon (Imp)")
           .replace("barrel_oil_us", "barrel (US oil)")
           .replace("barrel_beer_us", "barrel (US beer)")
           .replace("barrel_beer_uk", "barrel (UK beer)"))
    return lab

# ----------------------------
# SESSION STATE: history
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(obj):
    st.session_state.history.insert(0, obj)
    st.session_state.history = st.session_state.history[:500]

# ----------------------------
# LAYOUT: sidebar tools
# ----------------------------
st.sidebar.header("Tools / Pages")
tool = st.sidebar.radio("Choose tool", [
    "Unit Converter",
    "Number Bases (bin/oct/dec/hex)",
    "ASCII / Unicode",
    "Encodings & Hashes",
    "About & Suggest"
])

st.sidebar.markdown("---")
st.sidebar.caption("Session history is stored only while this tab is open. Use the 'Session History' link in the About page to download your history.")

# ----------------------------
# Helper: parse Decimal from input safely
# ----------------------------
def parse_decimal_input(text):
    text = text.strip()
    try:
        val = Decimal(text)
        return val
    except (InvalidOperation, ValueError):
        return None

# Helper: convert Decimal-valued quantity to pint Quantity
def quantity_from_decimal(value_decimal, unit_str):
    """
    Create a pint Quantity from a Decimal and unit string with high precision.
    """
    try:
        mp.dps = 50
        value_float = mp.mpf(str(value_decimal))
        q = Q_(float(value_float), unit_str)
        return q
    except Exception as e:
        st.error(f"Quantity creation error: {e}")
        return None

# Helper: format result with proper precision
def format_result(value, precision):
    """
    Format a numeric value with the specified precision.
    """
    try:
        if hasattr(value, 'magnitude'):
            value = value.magnitude
        if isinstance(value, Decimal):
            dec_val = value
        else:
            dec_val = Decimal(str(value))
        quantized = dec_val.quantize(Decimal('0.' + '0' * precision))
        return format(quantized, 'f').rstrip('0').rstrip('.')
    except:
        try:
            return f"{float(value):.{precision}f}".rstrip('0').rstrip('.')
        except:
            return str(value)

# ----------------------------
# TOOL: Unit Converter
# ----------------------------
if tool == "Unit Converter":
    st.header("🔀 Unit Converter")
    st.markdown(
        "Pick a category, choose units, and enter a numeric value. "
        "Conversions are aligned with NIST standards for high precision. "
        "Decimal input is supported; output precision is adjustable."
    )

    cat = st.selectbox("Category", list(CATEGORIES.keys()))
    units_for_cat = CATEGORIES[cat]
    labels = [pretty_unit_label(u) + f"  ({u})" for u in units_for_cat]

    col_a, col_b, col_c = st.columns([3, 3, 2])
    with col_a:
        from_choice = st.selectbox("From unit", labels, index=0)
        from_unit = units_for_cat[labels.index(from_choice)]
    with col_b:
        to_choice = st.selectbox("To unit", labels, index=1 if len(labels) > 1 else 0)
        to_unit = units_for_cat[labels.index(to_choice)]
    with col_c:
        raw_text = st.text_input("Value (Decimal allowed)", "1")
        prec = st.slider("Display precision (decimal places)", 3, 60, 8)
        convert_btn = st.button("Convert")

    if convert_btn:
        dec_val = parse_decimal_input(raw_text)
        if dec_val is None:
            st.error("Invalid numeric input. Use digits, optional decimal point, or scientific notation (e.g. 1.23e-4).")
        else:
            try:
                q_from = quantity_from_decimal(dec_val, from_unit)
                if q_from is None:
                    st.error("Failed to create quantity.")
                else:
                    q_to = q_from.to(to_unit)
                    formatted = format_result(q_to.magnitude, prec)
                    out_str = f"{dec_val} {from_unit} = {formatted} {to_unit}"
                    st.success(out_str)
                    add_history({
                        "tool": "unit",
                        "category": cat,
                        "from": from_unit,
                        "to": to_unit,
                        "value": str(dec_val),
                        "result": formatted
                    })
            except UndefinedUnitError as e:
                st.error(f"Undefined unit: {e}")
            except Exception as e:
                st.error(f"Conversion error: {e}")

# ----------------------------
# TOOL: Number Bases
# ----------------------------
elif tool == "Number Bases (bin/oct/dec/hex)":
    st.header("🔢 Number base conversions (binary / octal / decimal / hex)")
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        base_from = st.selectbox("From base", ["decimal", "binary", "octal", "hexadecimal"])
        input_text = st.text_input("Input value", "42")
    with col2:
        base_to = st.selectbox("To base", ["binary", "octal", "decimal", "hexadecimal"])
    with col3:
        if st.button("Convert"):
            def parse_base(s, base):
                s = s.strip()
                try:
                    if base == "decimal":
                        return int(s, 10)
                    if base == "binary":
                        return int(s, 2)
                    if base == "octal":
                        return int(s, 8)
                    if base == "hexadecimal":
                        return int(s, 16)
                except Exception:
                    return None
            n = parse_base(input_text, base_from)
            if n is None:
                st.error("Invalid input for selected base.")
            else:
                if base_to == "decimal":
                    out = str(n)
                elif base_to == "binary":
                    out = bin(n)[2:]
                elif base_to == "octal":
                    out = oct(n)[2:]
                elif base_to == "hexadecimal":
                    out = hex(n)[2:].upper()
                st.success(f"{input_text} ({base_from}) → {out} ({base_to})")
                add_history({"tool":"bases","from":base_from,"to":base_to,"input":input_text,"output":out})

# ----------------------------
# TOOL: ASCII / Unicode
# ----------------------------
elif tool == "ASCII / Unicode":
    st.header("🔡 ASCII / Unicode Code Points")
    sub = st.radio("Mode", ["ASCII table (0-127)", "Char → codes", "Code → Char (Unicode)"])
    if sub == "ASCII table (0-127)":
        df = []
        for i in range(128):
            ch = chr(i)
            display_char = ch if 32 <= i < 127 else ""
            df.append({
                "dec": i,
                "hex": hex(i)[2:].upper(),
                "oct": oct(i)[2:],
                "bin": bin(i)[2:].zfill(7),
                "char": display_char
            })
        st.dataframe(pd.DataFrame(df).set_index("dec"), width="stretch")
    elif sub == "Char → codes":
        s = st.text_input("Type characters (first character will be used)", "")
        if s != "":
            ch = s[0]
            st.write("Character:", html.escape(ch))
            st.write("Dec:", ord(ch))
            st.write("Hex:", hex(ord(ch))[2:].upper())
            st.write("Oct:", oct(ord(ch))[2:])
            st.write("Bin:", bin(ord(ch))[2:])
            add_history({"tool":"ascii_char","char":ch,"dec":ord(ch)})
    else:
        n = st.text_input("Enter Unicode code point (decimal)", "65")
        try:
            v = int(n)
            if 0 <= v <= 0x10FFFF:
                st.write("Char:", chr(v))
                add_history({"tool":"ascii_code","code":v,"char":chr(v)})
            else:
                st.error("Out of Unicode range.")
        except Exception:
            st.error("Invalid integer code point.")

# ----------------------------
# TOOL: Encodings & Hashes
# ----------------------------
elif tool == "Encodings & Hashes":
    st.header("🔐 Encodings, Hashes & Utilities")
    enc_sel = st.radio("Choose", ["Base64", "URL Encode/Decode", "Hashes (text/file)", "Text ↔ Hex/Bin"])

    if enc_sel == "Base64":
        txt = st.text_area("Text", "Hello world")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Encode Base64"):
                out = base64.b64encode(txt.encode("utf8")).decode("ascii")
                st.code(out)
                add_history({"tool":"base64","mode":"enc","in":txt,"out":out})
        with c2:
            if st.button("Decode Base64"):
                try:
                    dec = base64.b64decode(txt).decode("utf8")
                    st.code(dec)
                    add_history({"tool":"base64","mode":"dec","in":txt,"out":dec})
                except Exception:
                    st.error("Invalid Base64 input.")

    elif enc_sel == "URL Encode/Decode":
        txt = st.text_input("Text/URL", "https://example.com/?a=1 b")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("URL Encode"):
                out = urllib.parse.quote(txt, safe='')
                st.code(out)
                add_history({"tool":"url","mode":"enc","in":txt,"out":out})
        with c2:
            if st.button("URL Decode"):
                out = urllib.parse.unquote(txt)
                st.code(out)
                add_history({"tool":"url","mode":"dec","in":txt,"out":out})

    elif enc_sel == "Hashes (text/file)":
        sub = st.radio("Hash type", ["Text", "File"])
        if sub == "Text":
            text = st.text_input("Text to hash", "Hello")
            algo = st.selectbox("Algorithm", ["md5", "sha1", "sha256", "sha512"])
            if st.button("Hash Text"):
                h = hashlib.new(algo, text.encode("utf8")).hexdigest()
                st.code(h)
                add_history({"tool":"hash_text","algo":algo,"in":text,"out":h})
        else:
            f = st.file_uploader("Upload file to hash", type=None)
            algo = st.selectbox("Algorithm", ["md5", "sha1", "sha256", "sha512"], key="filehash_algo")
            if f is not None and st.button("Compute file hash"):
                hasher = hashlib.new(algo)
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
                h = hasher.hexdigest()
                st.code(h)
                add_history({"tool":"hash_file","filename":f.name,"algo":algo,"out":h})

    else:  # Text <-> Hex/Bin
        s = st.text_input("Text to convert", "Hello")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("To Hex"):
                hx = binascii.hexlify(s.encode("utf8")).decode("ascii").upper()
                st.code(hx)
                add_history({"tool":"tx2hex","in":s,"out":hx})
        with c2:
            if st.button("From Hex"):
                try:
                    txt = binascii.unhexlify(s).decode("utf8")
                    st.code(txt)
                    add_history({"tool":"hex2tx","in":s,"out":txt})
                except Exception:
                    st.error("Invalid hex input.")
        with c3:
            if st.button("To Bin"):
                bx = ''.join(format(b, '08b') for b in s.encode("utf8"))
                st.code(bx)
                add_history({"tool":"tx2bin","in":s,"out":bx})

# ----------------------------
# TOOL: About & Suggest
# ----------------------------
elif tool == "About & Suggest":
    st.header("ℹ️ About Units")
    st.markdown("""
    **Units** is a comprehensive conversion toolbox built with Streamlit and pint.
    - All conversions use NIST-aligned unit definitions for high precision (NIST Handbook 44, SP 811).
    - The app accepts high-precision Decimal input; output precision is adjustable via the slider.
    - Session history is kept only for the current browser tab; use the download buttons to persist history locally.
    """)
    st.markdown("### Suggest a unit (no API, no form data processed by this app)")
    st.write(
        "Clicking the button below will open a new GitHub Issue in your browser where you can file a suggestion. "
        "This is a safe redirect — no data is automatically sent from this app. "
        "You will be asked to sign in to GitHub if not already."
    )
    st.markdown(f"[Suggest a unit on GitHub]({GITHUB_ISSUE_URL})")
    st.markdown("---")
    st.markdown("### Session history & downloads")
    st.write("History is stored in-memory for the duration of your session/tab. Use the Session History page to download JSON/CSV before closing the tab.")

# ----------------------------
# GLOBAL: Session History Viewer / Download
# ----------------------------
st.sidebar.markdown("---")
if st.sidebar.button("Open Session History (download)"):
    st.session_state.show_history = True

if "show_history" in st.session_state and st.session_state.get("show_history"):
    st.header("🕘 Session History")
    if not st.session_state.history:
        st.info("No history yet. Perform some conversions or utilities to populate the session history.")
    else:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df.head(200), width="stretch")
        js = json.dumps(st.session_state.history, indent=2)
        st.download_button("⬇️ Download history (JSON)", data=js, file_name="units_history.json", mime="application/json")
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        keys = set()
        for row in st.session_state.history:
            keys.update(row.keys())
        keys = list(keys)
        writer.writerow(keys)
        for row in st.session_state.history:
            writer.writerow([row.get(k, "") for k in keys])
        st.download_button("⬇️ Download history (CSV)", data=csv_buf.getvalue(), file_name="units_history.csv", mime="text/csv")

# ----------------------------
# FOOTER / NOTES
# ----------------------------
st.markdown("---")
st.caption("Notes: 1) Conversions use NIST-aligned unit definitions (NIST Handbook 44, SP 811). 2) Decimal input is supported; output precision is adjustable. 3) Suggestions open a GitHub Issue — no data is transmitted from the app itself.")
