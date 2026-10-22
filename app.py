
import streamlit as st
import hashlib
import csv
import io
from pathlib import Path
from datetime import datetime
import database

st.set_page_config(
    page_title="Ransomware Detection System",
    page_icon="🛡️",
    layout="wide"
)

database.initialize_database()

st.title("🛡️ Ransomware Detection System")
st.write("Ransomware Detection and File Security Analysis")

st.warning(
    "Educational screening tool. No result guarantees a file is safe. "
    "Do not upload confidential files."
)

uploaded_file = st.file_uploader("Choose a file to scan")

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    filename = Path(uploaded_file.name).name
    extension = Path(filename).suffix.lower()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    st.subheader("File Analysis")
    st.write("File name:", filename)
    st.write("File size:", f"{len(file_bytes)} bytes")
    st.write("SHA-256:")
    st.code(file_hash)

    sample = file_bytes[:100000].decode(
        "utf-8", errors="ignore"
    ).lower()

    indicators = []

    if extension in {".locked", ".encrypted", ".crypt", ".wncry"}:
        indicators.append("Flagged file extension")

    for phrase in [
        "your files have been encrypted",
        "pay the ransom",
        "decrypt your files"
    ]:
        if phrase in sample:
            indicators.append("Possible ransom-note phrase: " + phrase)

    if indicators:
        result = "Suspicious indicators found"
        st.error(result)
    else:
        result = "No configured indicators found"
        st.info(result)

    for item in indicators:
        st.write("- ", item)

    if st.button("Save Scan to Database"):
        database.save_scan(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            filename,
            len(file_bytes),
            file_hash,
            result,
            "; ".join(indicators) if indicators else "None"
        )
        st.success("Scan saved to database.")

st.divider()
st.subheader("📊 Dashboard Statistics")

history = database.get_scans()

total_scans = len(history)
suspicious_scans = sum(
    1 for record in history
    if record["result"] == "Suspicious indicators found"
)
no_indicator_scans = sum(
    1 for record in history
    if record["result"] == "No configured indicators found"
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Scans", total_scans)
col2.metric("Suspicious Files", suspicious_scans)
col3.metric("No Indicators Found", no_indicator_scans)

st.divider()
st.subheader("📋 Scan History")

if history:
    st.dataframe(history, use_container_width=True)

    output = io.StringIO()
    fields = [
        "id", "scan_time", "filename", "file_size",
        "sha256", "result", "indicators"
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(history)

    st.download_button(
        "Download Scan Report (CSV)",
        data=output.getvalue(),
        file_name="ransomware_scan_report.csv",
        mime="text/csv"
    )
else:
    st.info("No scan history yet. Upload a file to begin.")
