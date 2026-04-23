import streamlit as st
from query import search_logs, build_attack_story
import pandas as pd
import re

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