# units.py
# Units — Universal Converter (Streamlit)
# Save as units.py and run with: streamlit run units.py

import streamlit as st
from decimal import Decimal, getcontext, InvalidOperation
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
import io, json, csv, hashlib, base64, binascii, urllib.parse, html
import pandas as pd

# ----------------------------
# CONFIG
# ----------------------------
# Decimal precision for parsing user input (high precision accepted)
getcontext().prec = 200  # user-visible decimal precision for input parsing & formatting

# GitHub Issue redirect (change these)
GITHUB_OWNER = "LiborBenes-US"   # <<-- change to your GitHub username
GITHUB_REPO = "Units"            # <<-- change to your repository name
ISSUE_TITLE = urllib.parse.quote("Unit suggestion:")
ISSUE_BODY = urllib.parse.quote(
    "Please describe the unit you'd like added (name, exact definition/ratio to SI unit, and source/reference).\n\nExample:\n- name: 'tablespoon_au'\n- definition: 20 mL\n- note: 'Australian tablespoon'"
)
GITHUB_ISSUE_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/new?title={ISSUE_TITLE}&body={ISSUE_BODY}"

# App meta
st.set_page_config(page_title="Units — Universal Converter", layout="wide", page_icon="⚖️")
st.title("Units — Universal Converter ⚖️")
st.markdown("**Converter: U.S. & Metric Units** — ad-free, comprehensive, and safe. Session history can be downloaded (only stored for current tab/session).")

# ----------------------------
# UNIT REGISTRY (pint) + extras
# ----------------------------
ureg = UnitRegistry()
Q_ = ureg.Quantity

# Extra (explicit) unit definitions (covering US survey, variants, barrels, cooking measures, bytes, etc.)
# We'll load these definitions into pint so they are explicit and labelled.
EXTRA_DEFS = """
# Survey / historical / labelled units
nautical_mile = 1852 * meter = nmi
statute_mile = 1609.344 * meter = mile
mile_us_survey = 1609.3472199999999 * meter
foot_us_survey = 1200/3937 * meter
acre_intl = 4046.8564224 * meter**2 = acre
acre_us_survey = 4046.8726099886 * meter**2
# Tons
ton_short = 2000 * pound = short_ton
ton_long = 2240 * pound = long_ton
tonne = 1000 * kilogram = t
quintal = 100 * kilogram = q
# Barrels and related
gallon_us = 231 * inch**3
fluid_ounce_us = gallon_us / 128
cup_us = 8 * fluid_ounce_us
pint_us = 2 * cup_us
quart_us = 2 * pint_us
fluid_ounce_imp = 28.4130625 * milliliter
pint_imp = 20 * fluid_ounce_imp
quart_imp = 2 * pint_imp
gallon_imp = 4 * pint_imp
# teaspoons/tablespoons (variants)
teaspoon_us = 4.92892159375 * milliliter
tablespoon_us = 14.78676478125 * milliliter
tablespoon_metric = 15 * milliliter
tablespoon_au = 20 * milliliter
# barrels (various)
barrel_oil_us = 42 * gallon_us
barrel_beer_us = 31 * gallon_us
barrel_beer_uk = 36 * gallon_imp
# Byte units - SI decimal and IEC binary prefixes
byte = [information]
kB = 1000 * byte
MB = 1000**2 * byte
GB = 1000**3 * byte
TB = 1000**4 * byte
PB = 1000**5 * byte
KiB = 1024 * byte
MiB = 1024**2 * byte
GiB = 1024**3 * byte
TiB = 1024**4 * byte
PiB = 1024**5 * byte
"""

# Load definitions into pint
import io as _io
for line in EXTRA_DEFS.splitlines():
    line = line.strip()
    if line and not line.startswith('#'):  # Skip empty lines and comments
        ureg.define(line)

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
    "Speed": ["meter/second", "kilometer/hour", "mile/hour", "knot"],
    "Pressure": ["pascal", "kilopascal", "bar", "atmosphere", "mmHg", "psi"],
    "Energy & Power": ["joule", "kilojoule", "watt*hour", "kilowatt*hour", "calorie", "kcal", "BTU", "watt"],
    "Fuel economy": ["liter/100 kilometer", "mile_per_gallon_us", "mile_per_gallon_imp"],
    "Digital storage": ["bit", "byte", "kB", "MB", "GB", "TB", "PB", "KiB", "MiB", "GiB", "TiB", "PiB"],
    "Angle": ["degree", "radian", "grad"]
}

# Utility: flatten units list for search dropdowns, with friendly labels
def pretty_unit_label(u):
    lab = u.replace("**2", "²").replace("**3", "³").replace("_", " ").replace("*", "·")
    return lab

# ----------------------------
# SESSION STATE: history
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts

def add_history(obj):
    st.session_state.history.insert(0, obj)
    # cap history length to avoid memory bloat
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
        # allow scientific notation; Decimal handles it
        val = Decimal(text)
        return val
    except (InvalidOperation, ValueError):
        return None

# Helper: convert Decimal-valued quantity to pint Quantity
def quantity_from_decimal(value_decimal, unit_str):
    """
    Attempts to create a pint Quantity from a Decimal and unit string.
    Pint may perform internal float conversions; we try to keep precision where possible.
    """
    try:
        # Some pint registries accept Decimal; create quantity directly
        q = Q_(value_decimal, unit_str)
        return q
    except Exception:
        # fallback: convert to float (loss of precision possible)
        return Q_(float(value_decimal), unit_str)

# ----------------------------
# TOOL: Unit Converter
# ----------------------------
if tool == "Unit Converter":
    st.header("🔀 Unit Converter")
    st.markdown(
        "Pick a category, choose units, and enter a numeric value. "
        "You may input very high-precision numbers (Decimal). "
        "Note: conversions use the pint library; very extreme precision may be limited by floating-point internals. "
    )

    cat = st.selectbox("Category", list(CATEGORIES.keys()))

    # build lists with readable labels
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

    # If user presses convert
    if convert_btn:
        dec_val = parse_decimal_input(raw_text)
        if dec_val is None:
            st.error("Invalid numeric input. Use digits, optional decimal point, or scientific notation (e.g. 1.23e-4).")
        else:
            # build quantities
            try:
                q_from = quantity_from_decimal(dec_val, from_unit)
                # attempt conversion
                q_to = q_from.to(to_unit)
                # format result: try to present using Decimal where possible
                # q_to.magnitude may be Decimal or float
                mag = q_to.magnitude
                # If it's a Decimal, format directly; if float, convert to Decimal for formatting
                if isinstance(mag, Decimal):
                    formatted = format(mag.quantize(Decimal(1) / (Decimal(10) ** prec)), 'f')
                else:
                    # convert to Decimal for rounding/formatting (may add floating rounding)
                    formatted = str(Decimal(mag).quantize(Decimal(1) / (Decimal(10) ** prec)))
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
    - All conversions are done using a curated pint registry (SI, metric subunits, US customary, Imperial, US survey, and other variants).
    - The app accepts high-precision numeric input (Decimal) but note conversions are performed by pint (floating-point internals may limit absolute precision).
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
        # show first 200 entries
        st.dataframe(df.head(200), width="stretch")
        # JSON download
        js = json.dumps(st.session_state.history, indent=2)
        st.download_button("⬇️ Download history (JSON)", data=js, file_name="units_history.json", mime="application/json")
        # CSV download
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        # flatten dicts to keys
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
st.caption("Notes: 1) This app uses pint for unit conversions. 2) Decimal input is supported; conversions may be subject to floating-point limits depending on unit factors. 3) Suggestions open a GitHub Issue — no data is transmitted from the app itself.")
