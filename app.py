import os

os.environ["TRANSFORMERS_VERBOSITY"] = "critical"

import streamlit as st

from transformers.utils import logging
logging.set_verbosity(50)
from query import search_logs, build_attack_story
import pandas as pd
import re

from datetime import datetime

from database.services.custody_service import (
    register_evidence,
    create_custody_event
)
from blockchain.blockchain_service import (
    register_evidence_on_blockchain,
    verify_evidence_integrity
)

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Security Dashboard", layout="wide")

# ---------------- FULL CSS (DARK + FIXED TEXT) ----------------
st.markdown("""
<style>

/* ---------------- BACKGROUND ---------------- */
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
}

/* Header */
[data-testid="stHeader"] {
    background: transparent;
}

/* ---------------- TEXT ---------------- */
.stMarkdown, p, span, label, div {
    color: white !important;
}

/* Titles */
.main-title {
    font-size: 45px;
    font-weight: bold;
    color: #38bdf8 !important;
}

.subtitle {
    color: #cbd5e1 !important;
}

/* ---------------- INPUT ---------------- */
input {
    color: black !important;
    background-color: white !important;
}

/* ---------------- BUTTON ---------------- */
.stButton button {
    background-color: #ef4444;
    color: white !important;
    font-size: 20px;
    padding: 10px 20px;
    border-radius: 12px;
}

/* ---------------- CARDS ---------------- */
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

/* ---------------- EXPANDER ---------------- */
[data-testid="stExpander"] {
    background-color: #020617 !important;
    border-radius: 10px;
}

[data-testid="stExpander"] * {
    color: white !important;
}

/* ---------------- FIX CODE BLOCK (PARTIAL) ---------------- */
[data-testid="stCodeBlock"] {
    background-color: #020617 !important;
}

/* ---------------- METRICS ---------------- */
h1, h2, h3 {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)
# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🛡️ AI Security Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time Log Forensic Analysis using RAG + LLM</div>', unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Controls")
top_k = st.sidebar.slider("Top Results", 1, 10, 5)

# ---------------- DIGITAL EVIDENCE ----------------

st.markdown("## 🔐 Digital Evidence Management")

case_id = st.text_input(
    "Case ID",
    value="CASE-001"
)

investigator_id = st.text_input(
    "Investigator ID",
    value="INV-001"
)

uploaded_file = st.file_uploader(
    "Upload Digital Evidence",
    type=["log", "txt", "csv"]
)

if uploaded_file:

    os.makedirs("evidence/original", exist_ok=True)

    evidence_path = os.path.join(
        "evidence/original",
        uploaded_file.name
    )

    st.info(f"Evidence file: {uploaded_file.name}")

    if st.button("🔐 Register Evidence"):

        # Save uploaded evidence ONLY when registering
        with open(evidence_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        evidence_id = (
            "EVD-" +
            datetime.now().strftime("%Y%m%d%H%M%S")
        )

        with st.spinner("Registering evidence..."):

            # 1. Create evidence object + SHA-256
            evidence = register_evidence(
                evidence_path,
                case_id,
                evidence_id,
                investigator_id
            )

            # 2. Register hash on blockchain
            blockchain_result = register_evidence_on_blockchain(
                evidence.evidence_id,
                evidence.case_id,
                evidence.sha256_hash,
                evidence.investigator_id
            )

            # 3. Create chain-of-custody event
            create_custody_event(
                evidence.evidence_id,
                "EVIDENCE_REGISTERED",
                evidence.investigator_id,
                "Evidence registered and SHA-256 hash stored on blockchain"
            )

        st.success("✅ Evidence registered successfully!")

        st.markdown("### 📋 Evidence Details")

        st.write("**Evidence ID:**", evidence.evidence_id)
        st.write("**Case ID:**", evidence.case_id)
        st.write("**Investigator:**", evidence.investigator_id)

        st.markdown("**SHA-256 Hash:**")
        st.code(evidence.sha256_hash)

        st.markdown("### ⛓️ Blockchain")

        st.write(
            "**Transaction:**",
            blockchain_result["transaction_hash"]
        )

        st.write(
            "**Block:**",
            blockchain_result["block_number"]
        )

        st.write(
            "**Contract:**",
            blockchain_result["contract_address"]
        )

        st.session_state["current_evidence"] = {
            "evidence_id": evidence.evidence_id,
            "file_path": evidence.file_path,
            "case_id": evidence.case_id,
            "investigator_id": evidence.investigator_id,
            "sha256_hash": evidence.sha256_hash,
            "transaction_hash": blockchain_result["transaction_hash"],
            "block_number": blockchain_result["block_number"],
            "contract_address": blockchain_result["contract_address"]
        }

                # Store custody event in session
        custody_event = create_custody_event(
            evidence.evidence_id,
            "EVIDENCE_REGISTERED",
            evidence.investigator_id,
            "Evidence registered and SHA-256 hash stored on blockchain"
        )

        st.session_state.setdefault("custody_events", [])
        st.session_state["custody_events"].append(custody_event)        

        st.success(
            "🔗 Evidence permanently registered on blockchain."
        )


# ---------------- VERIFY EVIDENCE ----------------

if "current_evidence" in st.session_state:

    st.divider()

    st.markdown("## 🔎 Evidence Integrity Verification")

    current_evidence = st.session_state["current_evidence"]

    if st.button("🛡️ Verify Evidence Integrity"):

        result = verify_evidence_integrity(
            current_evidence["file_path"],
            current_evidence["evidence_id"]
        )

        if result["verified"]:

            create_custody_event(
                current_evidence["evidence_id"],
                "INTEGRITY_VERIFIED",
                current_evidence["investigator_id"],
                "Evidence hash matched blockchain record"
            )

            custody_event = create_custody_event(
                current_evidence["evidence_id"],
                "INTEGRITY_VERIFIED",
                current_evidence["investigator_id"],
                "Evidence hash matched blockchain record"
            )

            st.session_state.setdefault("custody_events", [])
            st.session_state["custody_events"].append(custody_event)

            st.success(
                "✅ VERIFIED — Evidence integrity is intact."
            )

        else:

            create_custody_event(
                current_evidence["evidence_id"],
                "INTEGRITY_FAILED",
                current_evidence["investigator_id"],
                "Evidence hash does not match blockchain record"
            )

            custody_event = create_custody_event(
                current_evidence["evidence_id"],
                "INTEGRITY_FAILED",
                current_evidence["investigator_id"],
                "Evidence hash does not match blockchain record"
            )

            st.session_state.setdefault("custody_events", [])
            st.session_state["custody_events"].append(custody_event)

            st.error(
                "🚨 TAMPERED — Evidence has been modified!"
            )

        st.markdown("**Blockchain Hash:**")
        st.code(result["blockchain_hash"])

        st.markdown("**Current Hash:**")
        st.code(result["current_hash"])

# ---------------- CHAIN OF CUSTODY ----------------

if "custody_events" in st.session_state:

    st.divider()

    st.markdown("## 🔗 Chain of Custody")

    for event in st.session_state["custody_events"]:

        st.markdown(
            f"""
            <div class="card">
                <h3>🔐 {event.action}</h3>
                <b>Evidence ID:</b> {event.evidence_id}<br>
                <b>Investigator:</b> {event.investigator_id}<br>
                <b>Timestamp:</b> {event.timestamp}<br>
                <b>Description:</b> {event.description}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------- INPUT ----------------
query = st.text_input("🔍 Enter Query", placeholder="e.g. brute force attack")

# ---------------- BUTTON ----------------
if st.button("🚀 Analyze Threat"):

    if query:
        with st.spinner("🔍 Analyzing logs..."):

            # -------- SEARCH --------
            chunks = search_logs(query, top_k)

            # -------- EXTRACT IP DATA --------
            ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            ips = {}

            for chunk in chunks:
                for line in chunk.split("\n"):
                    matches = re.findall(ip_pattern, line)
                    for ip in matches:
                        ips[ip] = ips.get(ip, 0) + 1

            sorted_ips = sorted(ips.items(), key=lambda x: x[1], reverse=True)

            ip_list = [ip for ip, _ in sorted_ips[:5]]
            count_list = [count for _, count in sorted_ips[:5]]

            df = pd.DataFrame({
                "IP": ip_list,
                "Events": count_list
            })

            # ---------------- METRICS ----------------
            st.markdown("""
            <div style="background:#1e293b;padding:20px;border-radius:15px;">
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### 🚨 Total Events")
                st.markdown(f"<h1 style='color:#ef4444'>{sum(count_list)}</h1>", unsafe_allow_html=True)

            with col2:
                st.markdown("### 🌐 Unique IPs")
                st.markdown(f"<h1 style='color:#38bdf8'>{len(ip_list)}</h1>", unsafe_allow_html=True)

            with col3:
                st.markdown("### 🔥 Threat Level")
                st.markdown("<h1 style='color:#f97316'>HIGH</h1>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # -------- STATUS --------
            st.success("🟢 System Active | AI Monitoring Enabled")

            st.divider()

            # ---------------- MAIN LAYOUT ----------------
            left, right = st.columns([2, 1])

            # -------- LEFT (CHART) --------
            with left:
                st.markdown("### 📊 Suspicious IP Activity")

                if ip_list:
                    st.markdown("""
                    <div style="background:#1e293b;padding:20px;border-radius:15px;">
                    """, unsafe_allow_html=True)

                    st.bar_chart(df.set_index("IP"))

                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No suspicious IPs found")

            # -------- RIGHT (TOP IPS) --------
            with right:
                st.markdown("### 🚨 Top Threat Sources")

                for ip, count in sorted_ips[:5]:
                    st.markdown(f"""
                    <div class="card">
                        🌐 {ip} <br>
                        ⚠️ {count} events
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # ---------------- LOGS ----------------
            st.markdown("### 📄 Evidence Logs")

            for i, chunk in enumerate(chunks):
                with st.expander(f"Evidence {i+1}"):
                    st.markdown(f"""
<div style="
    background:#020617;
    color:#e2e8f0;
    padding:15px;
    border-radius:10px;
    font-family:monospace;
    font-size:14px;
    white-space:pre-wrap;
">
{chunk}
</div>
""", unsafe_allow_html=True)

            st.divider()

            # ---------------- AI REPORT ----------------
            st.markdown("### 🤖 AI Attack Report")

            story = build_attack_story(query, chunks)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.success(story)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---------------- ALERT ----------------
            st.error("🚨 CRITICAL THREAT DETECTED 🚨")

    else:
        st.warning("⚠️ Please enter a query")